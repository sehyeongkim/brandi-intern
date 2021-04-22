from flask import request, jsonify
from flask.views import MethodView
from flask_request_validator import validate_params, Param, GET, ValidRequest

from connection import get_connection

class OrderListView(MethodView):
    def __init__(self, service):
        self.service = service
    
    # 주문 조회
    # @login_required
    @validate_params(
        Param('date_from', GET, str, required=True),
        Param('date_to', GET, str, required=True),
        Param('sub_property_id', GET, int, required=False), # decorator에서 master인 경우에 True
        Param('order_number', GET, str, required=False),
        Param('order_status_id', GET, int, required=True),
        Param('order_detail_number', GET, str, required=False),
        Param('order_username', GET, str, required=False),
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
                order_list_result = self.service.get_order_list(conn, params)
            # return jsonify(order_list_result), 200
            return post_response(order_list_result), 200
        
        finally:
            conn.close()
    
    # order_status_type 변경
    # @login_required
    def patch(self):
        conn = None
        try:
            body = request.get_json()
            
            conn = get_connection()
                
            self.service.patch_order_status_type(conn, body)
                        
            conn.commit()
            
            # return jsonify({"message" : "SUCCESS"}), 200
            return get_response("SUCCESS"), 200
        
        finally:
            conn.close()



    def get(self, request):
        user_id = request.user
        