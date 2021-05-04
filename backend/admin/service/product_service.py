import random, string, uuid
from flask import g
from admin.model import ProductDao
from datetime import timedelta, datetime
from utils.custom_exception import StartDateFail, DataNotExists
import xlwt
from io import BytesIO
import copy
from connection import get_s3_connection

from utils.validation import (
                                validate_integer, 
                                validate_boolean, 
                                validate_datetime, 
                                validate_date,
                                validate_float, 
                                validate_string
)
from config import BUCKET_NAME, REGION
from utils.constant import (
                            START_DATE,
                            END_DATE,
                            PRODUCT_INFO_NOTICE
)


class ProductService:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.product_dao = ProductDao()
    
    # 상품 리스트 가져오기
    def get_products_list(self, conn, params, headers):
        # 페이지네이션 위한 OffSET 설정
        params['page'] = (params['page'] - 1) * params['limit']

        if 'end_date' in params:
            params['end_date'] +=  timedelta(days=1)
            params['end_date_str'] = params['end_date'].strftime('%Y-%m-%d')
        
        if 'start_date' in params:
            params['start_date_str'] = params['start_date'].strftime('%Y-%m-%d')
        
        if 'start_date' in params and 'end_date' in params and params['start_date'] > params['end_date']:
            raise  StartDateFail('조회 시작 날짜가 끝 날짜보다 큽니다.')
        
        # HEADERS로 엑셀파일 요청
        if 'application/vnd.ms-excel' in headers.values():
            result = self.product_dao.get_products_list(conn, params, headers)
            
            # 할인가격 key, value 추가
            for product in result:
                product['discount_price'] = product['price'] - (product['price'] * product['discount_rate'])
            
            output = BytesIO()

            workbook = xlwt.Workbook(encoding='utf-8')
            worksheet = workbook.add_sheet(u'시트1')
            worksheet.write(0, 0, u'등록일')
            worksheet.write(0, 1, u'대표이미지')
            worksheet.write(0, 2, u'상품명')
            worksheet.write(0, 3, u'상품코드')
            worksheet.write(0, 4, u'상품번호')
            worksheet.write(0, 5, u'셀러속성')
            worksheet.write(0, 6, u'셀러명')
            worksheet.write(0, 7, u'판매가')
            worksheet.write(0, 8, u'할인가')
            worksheet.write(0, 9, u'판매여부')
            worksheet.write(0, 10, u'할인여부')
            worksheet.write(0, 11, u'진열여부')

            idx = 1
            for row in result:
                worksheet.write(idx, 0, str(row['upload_date']))
                worksheet.write(idx, 1, row['image_url'])
                worksheet.write(idx, 2, row['title'])
                worksheet.write(idx, 3, row['product_code'])
                worksheet.write(idx, 4, row['id'])
                worksheet.write(idx, 5, row['sub_property'])
                worksheet.write(idx, 6, row['korean_brand_name'])
                worksheet.write(idx, 7, row['price'])
                worksheet.write(idx, 8, row['discount_price'])
                worksheet.write(idx, 9, ['판매' if row['is_selling'] else '미판매'])
                worksheet.write(idx, 10, ['할인' if row['discount_rate'] > 0 else '미할인'])
                worksheet.write(idx, 11, ['진열' if row['is_displayed'] else '미진열'])
                idx += 1
            
            workbook.save(output)
            output.seek(0)
            return output
        
        product_result, total_count_result = self.product_dao.get_products_list(conn, params, headers)
        
        # 할인가격 key, value 추가
        for product in product_result:
            product['discount_price'] = product['price'] - (product['price'] * product['discount_rate'])

        result = {
            'total_count' : total_count_result['total_count'],
            'product' : product_result
        }
        
        return result
    
    
    def create_product_info(self, conn, basic_info: dict, selling_info: dict):
        """상품 정보 validate, 생성

        필수 입력값, 선택 입력값을 validate 한 후
        dao에서 한번에 입력하기 위한 준비(null=true인 field에 None 할당)

        Args:
            conn (Connection): DB Connection Object
            basic_info (dict): 상품에 대한 정보(상품 이름, 상세 설명 등)
            selling_info (dict): 상품 판매에 대한 정보(가격, 할인율, 할인기간, 최대판매량, 최소판매량)

        Returns:
            product_id: 생성된 product의 id 반환
        """

        # 필수 입력값 validate
        validate_integer(basic_info['seller_id'])
        validate_integer(basic_info['property_id'])
        validate_integer(basic_info['category_id'])
        validate_integer(basic_info['sub_category_id'])
        validate_boolean(basic_info['is_selling'])
        validate_boolean(basic_info['is_displayed'])
        validate_string(basic_info['title'])
        validate_string(basic_info['content'])
        validate_integer(selling_info['price'])

        # 선택 입력값 존재하는 경우 validate

        # 상품 한줄 설명
        if 'simple_description' in basic_info:
            validate_string(basic_info['simple_description'])
        
        # 상품 정보 고시
        if 'manufacturer' in basic_info:
            validate_string(basic_info['manufacturer'])
        
        if 'date_of_manufacture' in basic_info:
            validate_string(basic_info['date_of_manufacture'])

        if 'origin' in basic_info:
            validate_string(basic_info['origin'])
        
        # 할인율
        if 'discount_rate' in  selling_info:
            validate_float(selling_info['discount_rate'])
        
        # 할인 기간 - 시작 날짜
        if 'discount_start_date' in selling_info:
            validate_datetime(selling_info['discount_start_date'])
        
        # 할인 기간 - 종료 날짜
        if 'discount_end_date' in selling_info:
            validate_datetime(selling_info['discount_end_date'])
        
        # 최소 판매 수량
        if 'min_amount' in selling_info:
            validate_integer(selling_info['min_amount'])
        
        # 최대 판매 수량
        if 'max_amount' in selling_info:
            validate_integer(selling_info['max_amount'])

        # params에 필수 데이터 할당 
        params = dict()
        params['seller_id'] = basic_info['seller_id']
        params['is_selling'] = basic_info['is_selling']
        params['is_displayed'] = basic_info['is_displayed']
        params['property_id'] = basic_info['property_id']
        params['category_id'] = basic_info['category_id']
        params['sub_category_id'] = basic_info['sub_category_id']
        params['title'] = basic_info['title']
        params['content'] = basic_info['content']
        params['price'] = selling_info['price']

        # params에 선택 데이터 할당
        params['simple_description'] = basic_info.get('simple_description', None)
        params['manufacturer'] = basic_info.get('manufacturer', PRODUCT_INFO_NOTICE)
        params['origin'] = basic_info.get('origin', PRODUCT_INFO_NOTICE)
        params['discount_rate'] = basic_info.get('discount_rate', 0)
        params['min_amount'] = basic_info.get('min_amount', 1)
        params['max_amount'] = basic_info.get('max_amount', 20)

        if 'discount_start_date' in selling_info:
            params['discount_start_date'] = validate_datetime(selling_info['discount_start_date'])
        else:
            params['discount_start_date'] = START_DATE
        

        if 'discount_end_date' in selling_info:
            params['discount_end_date'] = validate_datetime(selling_info['discount_end_date'])
        else:
            params['discount_end_date'] = END_DATE
        

        if 'date_of_manufacture' in basic_info:
            params['date_of_manufacture'] = validate_date(basic_info['date_of_manufacture'])
        else:
            params['date_of_manufacture'] = PRODUCT_INFO_NOTICE


        # 상품 코드 생성
        product_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
        params['product_code'] = product_code

        # products 테이블에 데이터 입력
        product_id = self.product_dao.create_product_info_dao(conn, params)

        # history 생성
        params['product_id'] = product_id
        params['modify_account_id'] = g.account_id
        self.product_dao.create_product_history(conn, params)
        
        return product_id

    def create_option_info(self, conn, product_id:int, option_info: list):
        """옵션 상품 정보 validate, 생성

        Args:
            conn (Connection): DB Connection Object
            product_id (int): 연결시킬 상위개념의 상품의 id
            option_info (list): 옵션 상품 리스트

        Returns:
            product_dao 계층의 create_option_history method
        """
        for option in option_info:

            # 필수 입력값 validate
            validate_integer(option['price'])

            # 선택 입력값 validate
            if 'stock' in option:
                validate_integer(option['stock'])
            
            if 'color_id' in option:
                validate_integer(option['color_id'])
            
            if 'size_id' in option:
                validate_integer(option['size_id'])

            # 입력값 setting
            option_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=25))
            option['color_id'] = option.get('color_id', None)
            option['size_id'] = option.get('size_id', None)
            option['stock'] = option.get('stock', None)
            option['product_id'] = product_id
            option['option_code'] = option_code

        option_ids = self.product_dao.create_option_info_dao(conn, option_info)

        # options_history 생성
        option_length = len(option_info)
        for i in range(option_length):
            option_info[i]['option_id'] = option_ids[i]
            option_info[i]['modify_account_id'] = g.account_id
            option_info[i]['is_deleted'] = 0
        
        return self.product_dao.create_option_history(conn, option_info)
    
    def upload_file_to_s3(self, img_obj, folder: str):
        s3_conn = get_s3_connection()
        uploaded_at = str(datetime.now())
        filename = img_obj.filename
        name = folder + uploaded_at + filename
        # 띄어쓰기, 콜론 등 필요없는 부분을 제거하기 위함
        key = name.replace(" ", "").replace(":","")
        s3_conn.upload_fileobj(Fileobj=img_obj,
                                Bucket=BUCKET_NAME,
                                Key=key)
        url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{key}"
        
        return url
    
    def insert_image_url(self, conn, product_id: int, imgs_obj: list):
        """image_url 생성 후 dao에서의 입력을 위해 

        Args:
            conn (Connection): DB Connection Object
            product_id (int): image가 해당되는 product_id
            imgs_obj (list): request로 받은 FileStorage Object list

        Returns:
            product_dao 계층의 insert_image_url_dao method
        """
        str_account_id = str(g.account_id)
        str_product_id = str(product_id)

        folder = f'product-images/{str_account_id}/{str_product_id}/'
        
        imgs_url = list()
        for img_obj in imgs_obj:
            url = self.upload_file_to_s3(img_obj, folder)
            imgs_url.append(url)
        
        params = list()

        for idx, val in enumerate(imgs_url):
    
            result = dict()
            result['image_url'] = val
            result['product_id'] = product_id
            result['created_account_id'] = g.account_id

            if idx == 0:
                result['is_represent'] = 1
            else:
                result['is_represent'] = 0
            
            params.append(result)
            
        return self.product_dao.insert_image_url_dao(conn, params)

    # 상품 리스트에서 상품의 판매여부, 진열여부 수정
    def patch_product_selling_or_display_status(self, conn, params):
        """상품 판매, 진열 수정 함수

        요청으로 들어온 JSON 으로 해당 상품의 진열, 판매 상태를 변경

        Args:
            conn (Connection): DB 커넥션 객체
            params (list):
                [
                    {"product_id" : 상품아이디, "selling" : 판매여부, "display" : 진열여부},
                    {"product_id" : 상품아이디, "selling" : 판매여부, "display" : 진열여부},
                    {"product_id" : 상품아이디, "selling" : 판매여부, "display" : 진열여부}
                    ...
                ]

        Returns:
            [list]: 변경하려는 상품이 데이터베이스에 존재하지 않거나 권한이 없는 경우의 상품리스트
        """
        # 데이터베이스 상품 조회 후 tuple 형태 변환
        product_check_results = tuple(map(lambda d:d.get('product_id'), self.product_dao.check_product_exists(conn, params)))
        
        # 해당 상품이 없거나 권한이 없을 경우 return
        if not product_check_results:
            return params

        # 데이터베이스에 없는 상품 리스트
        product_check_fail_result = list()
        
        # 데이터베이스에 있는 상품 리스트
        product_check_success_result = list()
        
        # 요청으로 들어온 값을 복합객체, 내용 복사
        requests_data = copy.deepcopy(params)

        # 요청으로 들어온 상품 과 데이터베이스 비교 후 리스트 분리
        for request_data in requests_data:
            if request_data.get('product_id') in product_check_results:
                product_check_success_result.append(request_data)
            else:
                product_check_fail_result.append(request_data)

        # 상품 판매, 진열 상태 변경
        self.product_dao.patch_product_selling_or_display_status(conn, product_check_success_result)
        
        # 상품 히스토리에 변경 이력 저장
        self.product_dao.insert_product_history(conn, product_check_success_result)

        return product_check_fail_result

    
    # 상품 상세 가져오기
    def get_product_detail(self, conn, params):
        """상품 코드로 상품 상세 조회 서비스

        상품코드로 상품정보, 상품이미지, 상품옵션 정보를 가져오고 결과 fomatting 수행

        Args:
            conn (Connection): DB 커넥션 객체
            params (dict)): { 'product_code' : PATH로 받은 상품코드 }

        Returns:
            [dict]]: product_detail = {
                        'basic_info': {
                            'product_id' : 상품아이디,
                            'product_code': 상품코드,
                            'selling': 판매여부,
                            'displayed': 진열여부,
                            'property': 셀러속성,
                            'category': 상품카테고리,
                            'sub_category': 상품하위카테고리,
                            'product_info_notice': {
                                'manufacturer': 제조사,
                                'date_of_manufacture': 제조일자,
                                'origin': 원산지
                            },
                            'title': 상품명,
                            'simple_description': 상품 한줄 설명,
                            'images': [
                                {
                                    'image_url' : 상품이미지 URL,
                                    'is_represent' : 대표상품 이미지 여부 1:대표, 0:대표아님
                                }
                            ],
                            'detail_description': 제품상세 설명
                        },
                        'option_info': [
                            {
                                'option_id': 옵션번호,
                                'color': 칼라,
                                'size': 사이즈,
                                'stock': 재고
                            }
                        ],
                        'selling_info': {
                            'price': 상품가격,
                            'discount_rate': 할인율,
                            'discount_price': 할인가격,
                            'discount_start_date': 할인 시작일,
                            'discount_end_date': 할인 끝일,
                            'min_amount': 최소판매수량,
                            'max_amount': 최대판매수량
                        }
                    }
        """
        product_result = self.product_dao.get_product_detail(conn, params)
        
        if not product_result:
            raise DataNotExists('상품을 조회할 수 없습니다.', 'product does not exists or Forbidden')

        product_image_result = self.product_dao.get_product_images_by_product_code(conn, params)

        if not product_image_result:
            raise DataNotExists('상품이미지를 조회할 수 없습니다.', 'product image does not exists or Forbidden')

        product_option_result = self.product_dao.get_product_options_by_product_code(conn, params)

        if not product_option_result:
            raise DataNotExists('상품옵션을 조회할 수 없습니다.', 'product option does not exists or Forbidden')

        product_detail = {
            'basic_info': {
                'seller_name' : product_result['seller_name'],
                'product_id' : product_result['product_id'],
                'product_code': product_result['product_code'],
                'is_selling': product_result['is_selling'],
                'is_displayed' : product_result['is_displayed'],
                'property_name': product_result['property'],
                'property_id': product_result['property_id'],
                'category': product_result['category'],
                'category_id': product_result['category_id'],
                'sub_category': product_result['sub_category'],
                'sub_category_id': product_result['sub_category_id'],
                'manufacturer': product_result['manufacturer'],
                'date_of_manufacture': product_result['date_of_manufacture'],
                'origin': product_result['origin'],
                'title': product_result['title'],
                'simple_description': product_result['simple_description'],
                'images': [
                    {
                        'image_url' : image['image_url'],
                        'is_represent' : image['is_represent']
                    }
                    for image in product_image_result
                ],
                'content': product_result['content']
            },
            'option_info': [
                {
                    'option_id': option['id'],
                    'color': option['color'],
                    'color_id': option['color_id'],
                    'size': option['size'],
                    'size_id': option['size_id'],
                    'stock': option['stock']
                }
            for option in product_option_result],
            'selling_info': {
                'price': product_result['price'],
                'discount_rate': product_result['discount_rate'],
                'discount_price': product_result['price'] - product_result['price'] * product_result['discount_rate'],
                'discount_start_date': product_result['discount_start_date'],
                'discount_end_date': product_result['discount_end_date'],
                'min_amount': product_result['min_amount'],
                'max_amount': product_result['max_amount']
            }
        }

        return product_detail
    
    # 상품 등록 창에서 seller 검색 master만 가능함
    def search_seller(self, conn, keyword:str):
        keyword = keyword + '%'
        params = dict()
        params['keyword'] = keyword
        return self.product_dao.search_seller_dao(conn, params)
    
    # seller 선택의 Response: seller 속성, 1차 카테고리
    def get_property_and_available_categories_list(self, conn, seller_id: int):
        params = dict()
        params['seller_id'] = seller_id
        return self.product_dao.get_property_and_available_categories_list_dao(conn, params)

    # 상품 sub categories list 출력
    def get_sub_categories_list(self, conn, category_id: int):
        params = dict()
        params['category_id'] = category_id
        return self.product_dao.get_sub_categories_list_dao(conn, params)
    
    # 상품 등록 창에서 color list 출력
    def get_products_color_list(self, conn):
        return self.product_dao.get_products_color_list_dao(conn)

    # 상품 등록 창에서 size list 출력
    def get_products_size_list(self, conn):
        return self.product_dao.get_products_size_list_dao(conn)
    
    # 상품 상세 설명에 들어가는 image url 
    def create_product_html_image_url(self, img_obj):
        str_account_id = str(g.account_id)
        folder = f'product-images-in-html/{str_account_id}/'
        url = self.upload_file_to_s3(img_obj, folder)
        return url
    
    # 상품등록 수정 patch
    def patch_products_info(self, conn, basic_info: dict, selling_info: dict):
        # 필수 입력값 validate
        validate_integer(basic_info['product_id'])
        validate_integer(basic_info['seller_id'])
        validate_integer(basic_info['property_id'])
        validate_integer(basic_info['category_id'])
        validate_integer(basic_info['sub_category_id'])
        validate_boolean(basic_info['is_selling'])
        validate_boolean(basic_info['is_displayed'])
        validate_string(basic_info['title'])
        validate_string(basic_info['content'])
        validate_integer(selling_info['price'])

        # 선택 입력값 존재하는 경우 validate

        # 상품 한줄 설명
        if 'simple_description' in basic_info:
            validate_string(basic_info['simple_description'])
        
        # 상품 정보 고시
        if 'manufacturer' in basic_info:
            validate_string(basic_info['manufacturer'])
        
        if 'date_of_manufacture' in basic_info:
            validate_date(basic_info['date_of_manufacture'])

        if 'origin' in basic_info:
            validate_string(basic_info['origin'])
        
        # 할인율
        if 'discount_rate' in  selling_info:
            validate_float(selling_info['discount_rate'])
        
        # 할인 기간 - 시작 날짜
        if 'discount_start_date' in selling_info:
            validate_datetime(selling_info['discount_start_date'])
        
        # 할인 기간 - 종료 날짜
        if 'discount_end_date' in selling_info:
            validate_datetime(selling_info['discount_end_date'])
        
        # 최소 판매 수량
        if 'min_amount' in selling_info:
            validate_integer(selling_info['min_amount'])
        
        # 최대 판매 수량
        if 'max_amount' in selling_info:
            validate_integer(selling_info['max_amount'])

        # params에 필수 데이터 할당 
        params = dict()
        params['product_id'] = basic_info['product_id']
        params['seller_id'] = basic_info['seller_id']
        params['is_selling'] = basic_info['is_selling']
        params['is_displayed'] = basic_info['is_displayed']
        params['property_id'] = basic_info['property_id']
        params['category_id'] = basic_info['category_id']
        params['sub_category_id'] = basic_info['sub_category_id']
        params['title'] = basic_info['title']
        params['content'] = basic_info['content']
        params['price'] = selling_info['price']

        # params에 선택 데이터 할당
        params['simple_description'] = basic_info.get('simple_description', None)
        params['manufacturer'] = basic_info.get('manufacturer', PRODUCT_INFO_NOTICE)
        params['origin'] = basic_info.get('origin', PRODUCT_INFO_NOTICE)
        params['discount_rate'] = basic_info.get('discount_rate', 0)
        params['min_amount'] = basic_info.get('min_amount', 1)
        params['max_amount'] = basic_info.get('max_amount', 20)

        # 시간 형식의 data는 datetime 형식으로 변환하여 할당
        if 'discount_start_date' in selling_info:
            params['discount_start_date'] = datetime.strptime(selling_info['discount_start_date'], '%Y-%m-%d %H:%M')
        else:
            params['discount_start_date'] = START_DATE
        

        if 'discount_end_date' in selling_info:
            params['discount_end_date'] = datetime.strptime(selling_info['discount_end_date'], '%Y-%m-%d %H:%M')
        else:
            params['discount_end_date'] = END_DATE
        

        if 'date_of_manufacture' in basic_info:
            # params['date_of_manufacture'] = validate_date(selling_info['date_of_manufacture'])
            params['date_of_manufacture'] = datetime.strptime(basic_info['date_of_manufacture'], '%Y-%m-%d')
        else:
            params['date_of_manufacture'] = PRODUCT_INFO_NOTICE
        
        # patch products info
        self.product_dao.patch_products_info(conn, params)

        # history 생성
        params['modify_account_id'] = g.account_id
        return self.product_dao.patch_products_history(conn, params)
    

    def patch_option_info(self, conn, product_id: int, option_info: list):
        # 기존 DB에 존재하는 option list
        exist_options = self.product_dao.get_options_by_product_id(conn, product_id)
        
        request_options = copy.deepcopy(option_info)
        
        # validate
        for request_option in request_options:

            # 필수 입력값 validate
            validate_integer(request_option['price'])

            # 선택 입력값 validate
            if 'stock' in request_option:
                validate_integer(request_option['stock'])
            
            if 'color_id' in request_option:
                validate_integer(request_option['color_id'])
            
            if 'size_id' in request_option:
                validate_integer(request_option['size_id'])
        

        # 들어온 요청(request_options)과 기존에 존재하는 option(exist_options)과 option_id 유무로 비교 후
        # 존재하면 request_option을 update_data 배열에 추가
        update_data = list()
        for exist_option in exist_options:
            for request_option in request_options:

                if 'option_id' in request_option:
                    if request_option['option_id'] == exist_option['option_id']:
                        update_data.append(request_option)
                        # update_data에 request_option 입력 후 request_options에서 삭제
                        # 비교대상인 exist_option도 exist_options에서 삭제
                        request_options.remove(request_option)
                        exist_options.remove(exist_option)
                        break


        # 기존에 존재하면서 업데이트된 options
        # 선택 입력값 setting
        for data in update_data:
            data['color_id'] = data.get('color_id', None)
            data['size_id'] = data.get('size_id', None)
            data['stock'] = data.get('stock', None)
        
        # 해당 option update
        self.product_dao.update_option_info(conn, update_data)

        # 업데이트한 내용 history 생성
        for data in update_data:
            data['modify_account_id'] = g.account_id
        self.product_dao.update_option_history(conn, update_data)


        # 새로 들어온 options
        # 선택 입력값 setting
        for request_option in request_options:

            option_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=25))
            request_option['option_code'] = option_code
            request_option['product_id'] = product_id
            request_option['color_id'] = request_option.get('color_id', None)
            request_option['size_id'] = request_option.get('size_id', None)
            request_option['stock'] = request_option.get('stock', None)
        
        
        # 새로 insert후 option의 id값들 list형태로 반환
        option_ids = self.product_dao.create_option_info_dao(conn, request_options)

        # history에 insert할 데이터에 새로 insert한 option의 id값 입력
        option_length = len(request_options)
        for i in range(option_length):
            request_options[i]['option_id'] = option_ids[i]
            request_options[i]['modify_account_id'] = g.account_id
            request_options[i]['is_deleted'] = 0
        
        # insert된 내용에 대한 history 생성
        self.product_dao.create_option_history(conn, request_options)


        # 삭제된 options
        # 지울 데이터 is_deleted = 1 설정
        self.product_dao.delete_option_info(conn, exist_options)

        # 지운 데이터 설정에 대한 history에 입력할 account_id setting
        for exist_option in exist_options:
            exist_option['modify_account_id'] = g.account_id
        
        # 지운 데이터 관련 history 생성
        self.product_dao.delete_option_history(conn, exist_options)


    def update_image_url(self, conn, product_id: int, imgs_obj: list): 
        # patch하면 product_id에 해당되는 값은 모두 is_deleted = 1로 하고 다 새롭게 insert해야 함
        
        # 기존의 db내용 deleted_account_id, deleted_at, is_deleted 세팅
        params = dict()
        params['product_id'] = product_id
        params['deleted_account_id'] = g.account_id
        params['deleted_at'] = datetime.now()
        params['is_deleted'] = 1
        self.product_dao.delete_images_in_product_images(conn, params)
        
        # img urls를 product_images에 insert
        self.insert_image_url(conn, product_id, imgs_obj)
