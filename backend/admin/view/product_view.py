from datetime import datetime

from flask import request, jsonify
from flask.views import MethodView
from flask_request_validator import validate_params, Param

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
        Param('sub_property', GET, str, required=False),
        Param('seller', GET, str, required=False),
        Param('product_id', GET, list, required=False),
        Param('product_name', GET, str, required=False),
        Param('product_code', GET, str, required=False),
        Param('product_number', GET, int, required=False),
        Param('page', GET, int, required=False),
        Param('limit', GET, int, required=False),
        Param('start_date', GET, str, rules=[datetime('%Y-%m-%d')]),
        Param('end_date', GET, str, rules=[datetime('%Y-%m-%d')])
    )
    def get(self, *args):
        conn = None
        try:
            params = dict()
            if args[0]:
                params['selling'] = args[0]
            
            if args[1]:
                params['discount'] = args[1]
            
            if args[2]:
                params['start_date'] = args[2]
            
            if args[3]:
                params['end_date'] = args[3]
            
            if args[4]:
                params['displayed'] = args[4]
            
            if args[5]:
                params['sub_property'] = args[5]
            
            if args[6]:
                params['seller'] = args[6]

            if args[7]:
                params['product_id'] = args[7]
            
            if args[8]:
                params['product_name'] = args[8]
            
            if args[9]:
                params['product_code'] = args[9]
            
            if args[10]:
                params['product_number'] = args[10]
            
            # pagination
            if args[11]:
                params[''] = args[11]
            
            if args[12]:
                params[''] = args[12]
            
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
            # request의 body 출력값 
            data = request.data   # type of data ??
            conn = get_connection()
            if conn:
                self.service.post_product_by_seller_or_master(conn, data)
                
            conn.commit()

            return jsonify(''), 200
        
        finally:
            conn.close()

    # 상품 리스트에서 상품의 판매여부, 진열여부 수정
    # @login_required
    def patch(self):
        conn = None
        try:
            data = request.data
            conn = get_connection()
            if conn:
                self.service.patch_product(conn, data)
            
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
        Params('search', GET, str, required=False)
    )
    def get(self, *args):
        conn = None
        try:
            conn = get_connection()
            if conn:
                result = self.service.search_seller(conn, *args)
            
            return jsonify(result), 200
        
        finally:
            conn.close()