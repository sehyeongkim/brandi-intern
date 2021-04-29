from model import ProductDao
from datetime import timedelta, datetime
from utils.custom_exception import StartDateFail, DataNotExists
import xlwt
from io import BytesIO
import copy

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
        if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in headers.values():
            result = self.product_dao.get_products_list(conn, params, headers)
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

        result = {
            'total_count' : total_count_result['total_count'],
            'product' : product_result
        }
        
        return result
    
    # 상품 등록 (by seller or master)
    def post_product_by_seller_or_master(self, conn, body):
        return self.product_dao.post_product_by_seller_or_master(conn, body)
    
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
                'product_code': product_result['product_code'],
                'selling': product_result['is_selling'],
                'displayed': product_result['is_displayed'],
                'property': product_result['property'],
                'category': product_result['category'],
                'sub_category': product_result['sub_category'],
                'product_info_notice': {
                    'manufacturer': product_result['manufacturer'],
                    'date_of_manufacture': product_result['date_of_manufacture'],
                    'origin': product_result['origin']
                },
                'title': product_result['title'],
                'simple_description': product_result['simple_description'],
                'images': [
                    {
                        'image_url' : image['image_url'],
                        'is_represent' : image['is_represent']
                    }
                for image in product_image_result],
                'detail_description': '<html>'
            },
            'option_info': [
                {
                    'option_id': option['id'],
                    'color': option['color'],
                    'size': option['size'],
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
    
    # 상품 categories list 가져오기
    def get_categories_list(self, conn, category_id):
        return self.product_dao.get_categories_list(conn, category_id)
    
    # sellers list 가져오기
    def get_sellers_list(self, conn, seller_id):
        return self.product_dao.get_seller_list(conn, seller_id)

    # 상품 등록 창에서 seller 검색
    def search_seller(self, conn, params):
        return self.product_dao.search_seller(conn, params)
    
    # 상품 등록 창에서 color list 뿌려주기
    def get_products_color_list(self, conn):
        return self.product_dao.get_products_color_list(conn)

    # 상품 등록 창에서 size list 뿌려주기
    def get_products_size_list(self, conn):
        return self.product_dao.get_products_size_list(conn)
