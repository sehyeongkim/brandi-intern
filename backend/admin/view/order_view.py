from flask import request, jsonify, g
from flask.views import MethodView
from flask_request_validator import validate_params, Param, GET, ValidRequest

from connection import get_connection
from utils import DecimalEncoder

class OrderView(MethodView):
    def __init__(self, service):
        self.service = service
    
    # 주문 조회
    # @login_required
    @validate_params(
        Param('date_from', GET, str, required=True),
        Param('date_to', GET, str, required=True),
        Param('sub_property', GET, str, required=False),
        Param('order_no', GET, str, required=True),
        Param('order_status_id', GET, int, required=True),
        Param('order_detail_no', GET, str, required=False),
        Param('user_name', GET, str, required=False),
        Param('phone', GET, str, required=False),
        Param('seller_name', GET, str, required=False),
        Param('product_name', GET, str, required=False)
    )
    def get(self, valid: ValidRequest):
        conn = None
        try:
            params = valid.get_params()
            conn = get_connection()
            if conn:
                result = self.service.get_order_list(conn, params)
            
            return jsonify(result), 200
        
        finally:
            conn.close()
    
    # order_status_type 변경
    # @login_required
    def patch(self):
        conn = None
        try:
            body = request.data
            conn = get_connection()
            if conn:
                self.service.patch_order_status_type(conn, body)
            
            conn.commit()
            
            return jsonify(''), 200
        
        finally:
            conn.close()

class DashboardSellerView(MethodView):
    def __init__(self, service):
        self.service = service
    
    #배송완료, 상품준비, 전체상품, 노출상품
    # @login_required
    def get(self):
        #account_id = g.account_id
        account_id=1
        conn = None
        try:
            conn = get_connection()
            results = self.service.get_dashboard_seller(conn, account_id)
            result = {"data" : results}
        # except Exception as e:
        #     return jsonify({'message': 'UNSUCCESS'}),400
        # else:
        #     return jsonify(result), 200
            return jsonify(result), 200        
        finally:
            conn.close()