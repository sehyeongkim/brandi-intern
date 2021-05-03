import bcrypt, jwt

from cachetools import TTLCache, cached
import time
from config import SECRET_KEY
from admin.model import AccountDao
from utils.custom_exception import SignUpFail, SignInError, TokenCreateError

from utils.formatter import CustomJSONEncoder

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

        # 캐시를 이용했을 때 시간을 측정
        # s = time.time()
        # print("status_type: ", time.time() -s)    
        return results

    def get_seller_list(self, conn, params):

        params['page'] = (params['page'] - 1) * params['limit']

        if 'end_date' in params:
            params['end_date'] +=  timedelta(days=1)
            params['end_date_str'] = params['end_date'].strftime('%Y-%m-%d')

        if 'start_date' in params:
            params['start_date_str'] = params['start_date'].strftime('%Y-%m-%d')

        if 'start_date' in params and 'end_date' in params and params['start_date'] > params['end_date']:
            raise  StartDateFail('조회 시작 날짜가 끝 날짜보다 큽니다.')

        seller_list, seller_count = self.account_dao.get_seller_list(conn, params)

        seller_list_info = {
            "seller_list": [
                {
                    "id": seller["seller_id"],
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
        self.account_dao.change_seller_status_type(conn, params)
        self.account_dao.change_seller_history(conn, params)

    def get_seller_info(self, conn, params):
        """셀러 상세 정보 formatting

        데이터베이스에서 가져온 셀러 정보를 dictionary 형태로 formatting하는 함수

        Args:
            conn (Connection): 데이터베이스 커넥션 객체
            params (dict): {"seller_identification" : 셀러 아이디

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
