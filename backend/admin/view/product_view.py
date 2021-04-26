from flask import request, jsonify, g, send_file
from flask.views import MethodView
from flask_request_validator import validate_params, Param, GET, Datetime, ValidRequest, CompositeRule, Min, Max, Enum, JsonParam, JSON, HEADER
from datetime import datetime
from connection import get_connection
from utils.response import get_response, post_response
from utils.custom_exception import IsInt, IsStr, IsFloat, IsRequired, DatabaseConnectFail
from flask_request_validator.exceptions import InvalidRequestError, RulesError
import xlwt

class ProductView(MethodView):
    def __init__(self, service):
        self.service = service
    # 상품 리스트 조회
    # @login_required
    @validate_params(
        Param('Content-Type', HEADER, str, required=False),
        Param('Authorization', HEADER, str, required=False),
        Param('selling', GET, int, required=False),
        Param('discount', GET, int, required=False),
        Param('start_date', GET, str, required=False),
        Param('end_date', GET, str, required=False),
        Param('displayed', GET, str, required=False),
        Param('sub_property', GET, list, required=False),
        Param('seller', GET, str, required=False),
        Param('product_name', GET, str, required=False),
        Param('product_code', GET, str, required=False),
        Param('product_number', GET, int, required=False),
        Param('page', GET, int, required=False, default=1, rules=[Min(1)]),
        Param('limit', GET, int, required=False, default=10, rules=[Enum(10, 20, 50)]),
        Param('start_date', GET, str, rules=[Datetime('%Y-%m-%d')], required=False),
        Param('end_date', GET, str, rules=[Datetime('%Y-%m-%d')], required=False),
        Param('select_product_id', GET, list, required=False)
    )
    def get(self, valid: ValidRequest):
        """상품 조회 리스트

        어드민 페이지의 상품관리 페이지에서 필터 조건에 맞는 주문 리스트가 출력됨.

        Args:
            conn (pymysql.connections.Connection): DB 커넥션 객체
            params (dict): 상품번호, 상품명, 상품코드, 판매여부, 진열여부 등의 정보가 담긴 딕셔너리

        Returns:
            {
                "result": {
                    "product": [
                        {
                            "discount_price": 할인가,
                            "discount_rate": 할인율,
                            "id": 상품번호,
                            "image_url": 이미지 URL,
                            "is_displayed": 진열여부,
                            "is_selling": 판매여부,
                            "korean_brand_name": 셀러명,
                            "price": 상품가격,
                            "product_code": 상품코드,
                            "seller_id": 셀러아이디,
                            "sub_property": 셀러구분,
                            "title": 상품명,
                            "upload_date": 등록일자
                        }
                    ],
                    "total_count": 총 상품 수
                },
                "status_code": 200
            }
            500: Exception
        """
        conn = None
        try:
            params = valid.get_params()
            headers = valid.get_headers()
            conn = get_connection()
            result = self.service.get_products_list(conn, params, headers)
            
            # HEADERS로 엑셀파일 요청
            if 'application/vnd.ms-excel' in headers.values():
                today = datetime.today().strftime('%Y-%m-%d')
                return send_file(result, attachment_filename=f'{today}product_list.xls', as_attachment=True)

            return get_response(result)

        finally:
            conn.close()
    
    # 상품 등록 (by master or seller)
    # @login_required
    def post(self, valid: ValidRequest):
        conn = None
        try:
            # request body의 data
            body = request.data
            params = valid.get_json()
            conn = get_connection()
            if conn:
                self.service.post_product_by_seller_or_master(conn, body)
                
            conn.commit()

            return jsonify(''), 200
        
        finally:
            conn.close()

    # 상품 리스트에서 상품의 판매여부, 진열여부 수정
    # @login_required
    def patch(self):
        conn = None
        try:
            # request body의 data
            body = request.data
            conn = get_connection()
            if conn:
                self.service.patch_product(conn, body)
            
            conn.commit()

            return jsonify(''), 200
        
        finally:
            conn.close()


class ProductDetailView(MethodView):
    def __init__(self, service):
        self.service = service

    # 상품 상세 가져오기
    # @login_required
    def get(self, product_code):
        conn = None
        try:
            conn = get_connection()
            if conn:
                result = self.service.get_product_detail(conn, product_code)
            
            return jsonify(result), 200
        
        finally:
            conn.close()


class ProductCategoryView(MethodView):
    def __init__(self, service):
        self.service = service

    # 상품 등록 -> 2차 카테고리 선택
    # @login_required
    def get(self, category_id):
        conn = None
        try:
            conn = get_connection()
            if conn:
                result = self.service.get_categories_list(conn, category_id)
            
            return jsonify(result), 200
        
        finally:
            conn.close()


class ProductSellerView(MethodView):
    def __init__(self, service):
        self.service = service
    
    # 상품 등록 -> 셀러 선택
    # @login_required
    def get(self, seller_id):
        conn = None
        try:
            conn = get_connection()
            if conn:
                result = self.service.get_sellers_list(conn, seller_id)
            
            return jsonify(result), 200
        
        finally:
            conn.close()


class ProductSellerSearchView(MethodView):
    def __init__(self, service):
        self.service = service

    # 상품 등록 -> 셀러 검색
    # @login_required
    @validate_params(
        Param('search', GET, str, required=False)
    )
    def get(self, valid: ValidRequest):
        conn = None
        try:
            params = valid.get_params()
            conn = get_connection()
            if conn:
                result = self.service.search_seller(conn, params)
            
            return jsonify(result), 200
        
        finally:
            conn.close()


class ProductColorView(MethodView):
    def __init__(self, service):
        self.service = service
    
    def get(self):
        conn = None
        try:
            conn = get_connection()
            if conn:
                result = self.service.get_products_color_list(conn)
            
            return jsonify(result), 200
        
        finally:
            conn.close()


class ProductSizeView(MethodView):
    def __init__(self, service):
        self.service = service
    
    def get(self):
        conn = None
        try:
            conn = get_connection()
            if conn:
                result = self.service.get_products_size_list(conn)
            
            return jsonify(result), 200
        
        finally:
            conn.close()