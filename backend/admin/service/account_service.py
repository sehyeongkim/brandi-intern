import bcrypt, jwt, xlwt

from flask import g
from cachetools import TTLCache, cached
import time
from config import SECRET_KEY
from admin.model import AccountDao
from utils.custom_exception import SignUpFail, SignInError, TokenCreateError, MasterLoginRequired
from utils.constant import MASTER, SELLER, USER, STORE_OUT, STORE_REJECTED
from utils.formatter import CustomJSONEncoder

from io import BytesIO

class AccountService:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.account_dao = AccountDao()

    def set_password_hash(self, params):
        params['password'] = bcrypt.hashpw(
            params['password'].encode('UTF-8'),
            bcrypt.gensalt()
        ).decode('UTF-8')
        
    def create_token(self, info):
        try:
            token = jwt.encode({"account_id": info['account_id']},
                                SECRET_KEY,
                                algorithm="HS256")
        except Exception as e:
            raise TokenCreateError("뜻하지 않은 에러가 발생했습니다. 다시 시도 해주세요.", "create_token error")
        
        return token
        
    def check_hash_password(self, conn, info, params):
        """ 로그인 hash password 체크하는 함수

        hash password 체크 후 account_type_id, accessToken값을 return하는 함수

        Args:
            conn (class): DB 클래스
            info (dict): post_account_login or post_master_login에서 가져온 계정 정보
            params (dict): BODY에서 넘어온 master or seller 정보

        Returns:
            [dict]: account_type_id , accessToken
        """
        if not info or not bcrypt.checkpw(params['password'].encode('utf-8'), info['password'].encode('utf-8')):
            raise SignInError("정확한 아이디, 비밀번호를 입력해주세요", "post_master_login error")
    
        account_type_id = self.account_dao.get_account_type_id(conn, info)
        token = self.create_token(info)
        return {
            "account_type_id" : account_type_id['account_type_id'],
            "accessToken" : token
        }
    #  ---------------------------------------------------------------------------------------------------------------------
    # account 회원가입
    def post_account_signup(self, conn, params):   
        checkid = self.account_dao.get_userid(conn, params)
        if checkid:
            raise SignUpFail("중복된 아이디 입니다.", "already_exist_id")
        
        # korean_brand_name 중복확인
        get_korean_brand_name = self.account_dao.get_korean_brand_name(conn, params)
        if get_korean_brand_name:
            raise SignUpFail("중복된 한글 브랜드 이름 입니다.", "already_exist_korean_brand_name")
        
        # english_brand_name 중복확인
        get_english_brand_name = self.account_dao.get_english_brand_name(conn, params)
        if get_english_brand_name:
            raise SignUpFail("중복된 영문 브랜드 이름 입니다.", "already_exist_english_brand_name")
        
        # password hash
        self.set_password_hash(params)
        
        # sub_property_id를 이용해서 property_id값을 가져오기
        get_property_id = self.account_dao.get_property_id(conn, params)
        if not get_property_id:
            raise SignUpFail("카테고리 선택에서 뜻하지 않은 에러가 발생했습니다.","get_property_id error")
        params['property_id'] = get_property_id['property_id']
        
        # account_type (seller = 2)
        params['account_type_id'] = 2
        
        # account 생성
        get_account_id = self.account_dao.create_account(conn, params)
        if not get_account_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "create_account error")
        params['account_id'] = get_account_id
        
        # seller 생성
        get_seller_id = self.account_dao.create_seller_signup(conn, params)
        params['seller_id'] = get_seller_id
        if not get_seller_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "create_seller_signup error")
        
        # manager 생성 ( seller id를 이용해서 )
        get_managers_id = self.account_dao.create_manager(conn, params)
        if not get_managers_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "crate_manager error")
        params['managers_id'] = get_managers_id
        
        # manager history 생성 ( get_managers_id를 이용해서 )
        get_manager_history_id = self.account_dao.create_managers_history(conn, params)
        if not get_manager_history_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "create_account_history error")
        
        # seller history 생성
        get_sellers_history_id = self.account_dao.create_seller_history(conn, params)
        if not get_sellers_history_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "create_seller_history error")
        
    # seller 로그인
    def post_account_login(self, conn, params):
        seller_info = self.account_dao.post_account_login(conn, params)
        result = self.check_hash_password(conn, seller_info, params)
        
        return result
    
    # master 로그인
    def post_master_login(self, conn, params):
        master_info = self.account_dao.post_master_login(conn, params)
        result = self.check_hash_password(conn, master_info, params)
        
        return result
        
    def create_token(self, seller_info):
        token = jwt.encode({"account_id": seller_info['account_id']},
                                SECRET_KEY,
                                algorithm="HS256")
        # encode 예외 처리 찾으면 try 문 사용해서 추가 할 수 있도록
        # raise TokenCreateError("뜻하지 않은 에러가 발생했습니다. 다시 시도 해주세요.", "create_token error")
        return token

    @cached(cache = TTLCache(12, 10))
    def get_status_type(self, conn, seller_status_type):
        """셀러 상태를 가져오는 함수

        DB로부터 입점, 휴점, 퇴점 등 셀러의 상태 관련 데이터를 가져오는 함수

        Args:
            conn (Connection): DB커넥션 객체
            seller_status_type (str): 현재 셀러의 입점 상태

        Returns:
            results (list): 
                [
                    {
                        'button_name': 버튼 이름, 
                        'to_status_type_id': 버튼을 클릭하면 이동하는 상태 id
                    }, 
                    {
                        'button_name': 버튼 이름, 
                        'to_status_type_id': 버튼을 클릭하면 이동하는 상태 id
                    }
                ]
        """
        # status_name, seller_status_type_id, button_id, button_name, to_status_type_id가 포함된 리스트        
        seller_status_type_button_lists = self.account_dao.get_seller_status(conn, seller_status_type)

        results = list()
        for seller_status_type_button in seller_status_type_button_lists:
            if seller_status_type in ["입점신청", "입점", "휴점", "퇴점대기"]:
                seller_button_info = {
                                        "button_name": seller_status_type_button["button_name"], 
                                        "to_status_type_id": seller_status_type_button["to_status_type_id"]
                                    }
                results.append(seller_button_info)
            elif seller_status_type in ["입점거절", "퇴점"]:
                continue
        
        return results

    def get_seller_list(self, conn, params, headers):
        """셀러 계정 리스트

        특정 조건(params)에 따라서 표출되는 셀러 계정 리스트

        Args:
            conn (Connection): DB커넥션 객체
            params (dict): 
                {
                    'page': 페이지,
                    'limit': 노출 개수,
                    'seller_id': 셀러 pk 번호,
                    'seller_identification': 셀러 아이디,
                    'english_brand_name': 셀러 영문 브랜드명,
                    'korean_brand_name': 셀러 한글 브랜드명,
                    'manager_name': 담당자 이름,
                    'seller_status_type': 셀러 현재 입점 상태,
                    'manager_phone': 담당자 전화번호,
                    'manager_email': 담당자 이메일,
                    'sub_property': 셀러 2차속성,
                    'seller_created_date': 셀러 생성일
                }
            headers (dict): 
                {
                    'Content-Type': 'application/vnd.ms-excel'
                }

        Raises:
            StartDateFail: 조회 시작 날짜가 끝 날짜보다 클 경우 발생하는 에러

        Returns:
           seller_list_info (list) : 
                [
                    {
                        "seller_id": 셀러 pk번호,
                        "seller_identification": 셀러 아이디,
                        "english_brand_name": 셀러 한글 브랜드명,
                        "korean_brand_name": 셀러 영어 브랜드명,
                        "manager_name": 담당자 이름,
                        "seller_status_type": 셀러 입점 상태,
                        "seller_status_type_button": 셀러 입점 상태 변경 버튼,
                        "manager_phone": 담당자 전화번호,
                        "manager_email": 담당자 이메일,
                        "sub_property": 셀러 2차 속성,
                        "seller_created_date": 셀러 생성 날짜
                    } for seller in seller_list
                ],
                "total_count": seller_count["count"]
        """

        params['offset'] = (params['page'] - 1) * params['limit']

        if 'end_date' in params:
            params['end_date'] +=  timedelta(days=1)
            params['end_date_str'] = params['end_date'].strftime('%Y-%m-%d')

        if 'start_date' in params:
            params['start_date_str'] = params['start_date'].strftime('%Y-%m-%d')

        if 'start_date' in params and 'end_date' in params and params['start_date'] > params['end_date']:
            raise  StartDateFail('조회 시작 날짜가 끝 날짜보다 큽니다.')

        # HEADERS로 엑셀파일 요청
        if 'application/vnd.ms-excel' in headers.values():
            seller_info_list = self.account_dao.get_seller_list(conn, params, headers)
            output = BytesIO()

            workbook = xlwt.Workbook(encoding='utf-8')
            worksheet = workbook.add_sheet(u'시트1')
            worksheet.write(0, 0, u'번호')
            worksheet.write(0, 1, u'셀러아이디')
            worksheet.write(0, 2, u'영문이름')
            worksheet.write(0, 3, u'한글이름')
            worksheet.write(0, 4, u'담당자이름')
            worksheet.write(0, 5, u'셀러상태')
            worksheet.write(0, 6, u'담당자연락처')
            worksheet.write(0, 7, u'담당자이메일')
            worksheet.write(0, 8, u'셀러속성')
            worksheet.write(0, 9, u'등록일시')

            idx = 1
            for row in seller_info_list:
                worksheet.write(idx, 0, row['seller_id'])
                worksheet.write(idx, 1, row['seller_identification'])
                worksheet.write(idx, 2, row['english_brand_name'])
                worksheet.write(idx, 3, row['korean_brand_name'])
                worksheet.write(idx, 4, row['manager_name'])
                worksheet.write(idx, 5, row['seller_status_type'])
                worksheet.write(idx, 6, row['manager_phone'])
                worksheet.write(idx, 7, row['manager_email'])
                worksheet.write(idx, 8, row['sub_property'])
                worksheet.write(idx, 9, str(row['seller_created_date']))
                idx += 1
            
            workbook.save(output)
            output.seek(0)
            return output

        seller_list, seller_count = self.account_dao.get_seller_list(conn, params)

        seller_list_info = {
            "seller_list": [
                {
                    "seller_id": seller["seller_id"],
                    "seller_identification": seller["seller_identification"],
                    "english_brand_name": seller["english_brand_name"],
                    "korean_brand_name": seller["korean_brand_name"],
                    "manager_name": seller["manager_name"],
                    "seller_status_type": seller["seller_status_type"],
                    "seller_status_type_button": self.get_status_type(conn, seller["seller_status_type"]),
                    "manager_phone": seller["manager_phone"],
                    "manager_email": seller["manager_email"],
                    "sub_property": seller["sub_property"],
                    "seller_created_date": seller["seller_created_date"]
                } for seller in seller_list
            ],
            "total_count": seller_count["count"]
        }
        return seller_list_info
    
    def change_seller_status_type(self, conn, params):
        """셀러 상태 변경 함수

        셀러의 상태 변경 버튼을 누를 시, 셀러의 입점상태가 변경되는 함수

        Args:
            conn (Connection): DB커넥션 객체
            params (dict): 
                {
                    'to_status_type_id': 변경될 셀러 상태 번호, 
                    'account_id': 회원 pk 번호, 
                    'seller_id': 셀러 pk 번호
                }
        """
        self.account_dao.change_seller_status_type(conn, params)
        
        if self.account_dao.check_if_store_out(conn, params)["seller_status_type_id"] in [STORE_REJECTED, STORE_OUT]:
            self.account_dao.change_seller_is_deleted(conn, params)
        self.account_dao.change_seller_history(conn, params)


    def get_seller_info(self, conn, params):
        """셀러 상세 정보 formatting

        데이터베이스에서 가져온 셀러 정보를 dictionary 형태로 formatting하는 함수

        Args:
            conn (Connection): DB커넥션 객체
            params (dict): {"seller_identification" : 셀러 아이디}

        Returns:
            seller_result (dict): 셀러 정보가 formatting된 결과
                seller_result = {
                    "profile_image_url": 셀러 프로필 이미지,
                    "seller_status_type": 셀러 계정 입점 상태,
                    "korean_brand_name": 한글 브랜드명,
                    "english_brand_name": 영어 브랜드명,
                    "seller_identification": 셀러아이디,
                    "background_image_url": 배경이미지,
                    "seller_description": 셀러 설명,
                    "seller_detail_description": 셀러 상세 설명,
                    "customer_center": 고객센터,
                    "customer_center_phone": 고객센터 전화번호,
                    "zip_code": 우편번호,
                    "address": 셀러 주소,
                    "detail_address": 셀러 상세 주소,
                    "customer_open_time": 고객센터 운영 시작 시간,
                    "customer_close_time": 고객센터 운영 끝 시간,
                    "delivery_info": 배송 정보,
                    "exchange_refund_info": 교환/환불 정보,
                    "manager_info_list": [
                        {
                            "manager_name": 담당자 이름,
                            "manager_phone": 담당자 전화번호,
                            "manager_email": 담당자 이메일
                        }
                        for manager in manager_info
                    ]
                }
        """
        seller_info, manager_info = self.account_dao.get_seller_info(conn, params)

        seller_result = {
            "profile_image_url": seller_info["profile_image_url"],
            "seller_status_type": seller_info["seller_status_type"],
            "korean_brand_name": seller_info["korean_brand_name"],
            "seller_status_type_id": seller_info["seller_status_type_id"],
            "english_brand_name": seller_info["english_brand_name"],
            "seller_identification": seller_info["seller_identification"],
            "background_image_url": seller_info["background_image_url"],
            "seller_description": seller_info["description"],
            "seller_detail_description": seller_info["detail_description"],
            "customer_center": seller_info["customer_center"],
            "customer_center_phone": seller_info["customer_center_number"],
            "zip_code": seller_info["zip_code"],
            "address": seller_info["address"],
            "detail_address": seller_info["detail_address"],
            "customer_open_time": seller_info["open_at"],
            "customer_close_time": seller_info["close_at"],
            "delivery_info": seller_info["delivery_info"],
            "exchange_refund_info": seller_info["exchange_refund_info"],
            "manager_info_list": [
                {
                    "manager_name": manager["manager_name"],
                    "manager_phone": manager["manager_phone"],
                    "manager_email": manager["manager_email"]
                }
                for manager in manager_info
            ]
        }

        return seller_result


    def update_seller_info(self, conn, params, manager_params):
        """셀러 수정 

        셀러의 정보를 수정하는 함수

        Args:
            conn (Connection): DB커넥션 객체
            params (dict): 
                {
                    'profile_image_url': 셀러 프로필 이미지, 
                    'background_image_url': 배경 이미지, 
                    'seller_sub_property': 셀러 2차 속성, 
                    'seller_sub_property_id': 2차 속성 id, 
                    'korean_brand_name': 셀러 한글 브랜드명, 
                    'english_brand_name': 셀러 영어 브랜드명, 
                    'description': 한 줄 소개, 
                    'detail_description': 상세 소개, 
                    'zip_code': 우편번호, 
                    'address': 주소, 
                    'detail_address': 상세주소, 
                    'customer_center': 고객센터, 
                    'customer_center_phone': 고객센터 전화번호, 
                    'customer_open_time': 고객센터 시작 시간, 
                    'customer_close_time': 고객센터 마감 시간, 
                    'delivery_info': 배송 정보, 
                    'exchange_refund_info': 교환/환불 정보, 
                    'account_id': 계정 id, 
                    'account_type_id': 계정 type id, 
                    'seller_id': 셀러 id
                }
            manager_params (list):     
                "manager_info_list": 
                [
                    {
                        "manager_name": 매니저,
                        "manager_email": 매니저 이메일,
                        "manager_phone": 매니저 전화번호
                    },
                    {
                        "manager_name": 매니저2,
                        "manager_email": 매니저2 이메일,
                        "manager_phone": 매니저2 전화번호
                    }
                ],

        Raises:
            MasterLoginRequired: 셀러로 로그인시 변경 권한이 없는 정보를 수정하려 했을 때
        """

        # 마스터인지 셀러인지 확인
        # 셀러인 경우 들어오면 안되는 정보들은 막아줌
        if params.get("account_type_id") == SELLER:
            if params.get("seller_sub_property") or params.get("seller_sub_property_id") or params.get("korean_brand_name") or params.get("english_brand_name"):
                raise MasterLoginRequired("수정 권한이 없습니다.")

        # db에 있는 현재 담당자
        current_managers_in_db = self.account_dao.get_managers_info(conn, params)
        # 현재 db에 있는 manager_id를 요청값에 추가하기 위함
        for i, manager_info in enumerate(manager_params):
            for j, current_manager_in_db in enumerate(current_managers_in_db):
                if i == j:
                    manager_info["manager_id"] = current_manager_in_db["manager_id"]
                    continue
        
        # db에 있는 담당자수가 더 많을 때 -> 삭제해야 함
        if len(current_managers_in_db) > len(manager_params):
            # 요청값을 기준으로 수정, 삭제할 개수 정하기
            self.account_dao.update_managers_info(conn, manager_params[:len(manager_params)])
            self.account_dao.insert_managers_history(conn, manager_params[:len(manager_params)])

            # db에 담당자 수가 많을 경우에는 account_id가 필요함
            for current_manager_in_db in current_managers_in_db:
                current_manager_in_db["account_id"] = g.account_id
            self.account_dao.delete_managers_info(conn, current_managers_in_db[len(manager_params):])
            self.account_dao.insert_managers_history(conn, current_managers_in_db[len(manager_params):])

        
        # db에 있는 담당자수와 요청 수가 같을 때 -> 수정만 함
        elif len(current_managers_in_db) == len(manager_params):
            self.account_dao.update_managers_info(conn, manager_params)
        
        # db에 있는 담당자수가 더 적을 때 -> 추가해야 함
        else:
            # 현재 db에 있는 담당자 수를 기준으로 수정, 추가할 개수 정하기
            self.account_dao.update_managers_info(conn, manager_params[:len(current_managers_in_db)])
            self.account_dao.insert_managers_info(conn, manager_params[len(current_managers_in_db):])
            self.account_dao.insert_managers_history(conn, manager_params[len(current_managers_in_db):])

        # 셀러 정보 수정 & 셀러 history 추가
        self.account_dao.update_seller_info(conn, params)
        self.account_dao.insert_seller_history(conn, params)