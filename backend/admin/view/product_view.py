from flask import request, jsonify, g
from flask.views import MethodView
from flask_request_validator import validate_params, Param, GET, Datetime, ValidRequest, CompositeRule, Min, Max, Enum
from datetime import datetime
from connection import get_connection


class ProductView(MethodView):
    def __init__(self, service):
        self.service = service

    # 상품 리스트 조회
    # @login_required
    @validate_params(
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
        Param('end_date', GET, str, rules=[Datetime('%Y-%m-%d')], required=False)
    )
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
    # @login_required 
    def post(self):
        conn = None
        try:
            # request body의 data
            body = request.data
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