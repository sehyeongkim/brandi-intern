from flask import request, jsonify, g
from flask.views import MethodView
from flask_request_validator import validate_params, Param, GET, Datetime, ValidRequest

from utils.custom_exception import DatabaseCloseFail, DatabaseConnectFail, RequiredDataError

from connection import get_connection, get_s3_connection
from config import BUCKET_NAME

class ProductView(MethodView):
    def __init__(self, service):
        self.service = service

    # 상품 리스트 조회
    def get(self, valid: ValidRequest):
        conn = None
        try:
            params = valid.get_params()
            conn = get_connection()
            if conn:
                result = self.service.get_products_list(conn, params)
            
            return jsonify(result), 200
        
        finally:
            conn.close()

    # 상품 등록 (by master or seller)
    # @login_required -------> seller or master
    @validate_params(
    JsonParam({
        'basic_info' : JsonParam({
            "seller_id" : [IsInt()],
            "is_selling" : [IsInt()],
            "is_displayed" : [IsInt()],
            "property_id" : [IsInt()],
            "category_id" : [IsInt()],
            "sub_category_id" : [IsInt()],
            "product_info_notice" : JsonParam({
                "manufacturer" : [IsStr()],
                "date of manufacture" : [IsStr()],
                "origin" : [IsStr()]
            }),
            "title" : [IsStr()],
            "description" : [IsStr()],
            "content" : [IsStr()]
        }, required=True),
        "option_info" : JsonParam({
            "color_id" : [IsInt()],
            "size_id" : [IsInt()],
            "stock" : [IsInt()]
        }, as_list=True, required=True),
        "selling_info" : JsonParam({
            "price" : [IsInt()],
            "discount_rate" : [IsFloat()],
            "discount_start_date" : [Datetime('%Y-%m-%d %H:%M')],
            "discount_end_date" : [Datetime('%Y-%m-%d %H:%M')],
            "min_amount" : [IsInt()],
            "max_amount" : [IsInt()]
        }, required=True),
    })
    )   
    def post(self, valid: ValidRequest):
        conn = None
        try:
            body = valid.get_json()

            basic_info = body['basic_info']
            selling_info = body['selling_info']
            option_info = body['option_info'] if body['option_info'] else None
            files = request.form.getlist('image')
            
            conn = get_connection()

            if not conn:
                raise DatabaseConnectFail('서버와 연결할 수 없습니다.')
            
            # create basic information
            product_id = self.service.create_basic_info(conn, basic_info)

            # create selling information
            self.service.create_selling_info(conn, selling_info)

            # create options if exists
            if option_info:
                self.service.create_option_info(conn, product_id, option_info)
            
            #upload image to s3
            self.service.create_image_url(conn, product_id, files)
            
            conn.commit()
        
            return "SUCCESS"
        
        except Exception:
            conn.rollback()

        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    conn.rollback()
                    raise DatabaseCloseFail('서버와 연결을 끊는 도중 알 수 없는 에러가 발생했습니다.')
    
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


class ProductSellerSearchView(MethodView):
    def __init__(self, service):
        self.service = service

    # 상품 등록 -> 셀러 검색
    @validate_params(
        Param('search', GET, str, required=False)
    )
    def get(self, valid: ValidRequest):
        conn = None
        try:
            params = valid.get_params()
            keyword = params['search']
            conn = get_connection()
            if not conn:
                raise DatabaseConnectFail('서버와 연결할 수 없습니다.')
            
            return self.service.search_seller(conn, keyword)

        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    raise DatabaseCloseFail('서버와 연결을 끊는 도중 알 수 없는 에러가 발생했습니다.')


class ProductSellerView(MethodView):
    def __init__(self, service):
        self.service = service
    
    # 상품 등록 -> 셀러 선택
    # seller 속성, 1차 카테고리
    def get(self, seller_id):
        conn = None
        try:
            conn = get_connection()
            if not conn:
                raise DatabaseConnectFail('서버와 연결할 수 없습니다.')
            
            return self.service.get_property_and_available_categories(conn, seller_id)
        
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    raise DatabaseCloseFail('서버와 연결을 끊는 도중 알 수 없는 에러가 발생했습니다.')


class ProductSubCategoryView(MethodView):
    def __init__(self, service):
        self.service = service
    
    # 상품 등록 -> 2차 카테고리 선택
    def get(self, category_id):
        conn = None
        try:
            conn = get_connection()
            if not conn:
                raise DatabaseConnectFail('서버와 연결할 수 없습니다.')

            return self.service.get_sub_categories_list(conn, category_id)
        
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    raise DatabaseCloseFail('서버와 연결을 끊는 도중 알 수 없는 에러가 발생했습니다.')


class ProductColorView(MethodView):
    def __init__(self, service):
        self.service = service
    
    def get(self):
        conn = None
        try:
            conn = get_connection()
            if not conn:
                raise DatabaseConnectFail('서버와 연결할 수 없습니다.')

            return self.service.get_products_color_list(conn)
        
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    raise DatabaseCloseFail('서버와 연결을 끊는 도중 알 수 없는 에러가 발생했습니다.')


class ProductSizeView(MethodView):
    def __init__(self, service):
        self.service = service
    
    def get(self):
        conn = None
        try:
            conn = get_connection()
            if not conn:
                raise DatabaseConnectFail('서버와 연결할 수 없습니다.')

            return self.service.get_products_size_list(conn)
        
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    raise DatabaseCloseFail('서버와 연결을 끊는 도중 알 수 없는 에러가 발생했습니다.')