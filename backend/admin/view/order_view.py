from flask import request, jsonify
from flask.views import MethodView
from flask_request_validator import validate_params, Param

from connection import get_connection

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
    def get(self, *args):
        conn = None
        try:
            params = dict()
            params['date_from'] = args[0]
            params['date_to'] = args[1]
            params['order_no'] = args[3]
            params['order_status_id'] = args[4]

            if args[2]:
                params['sub_property'] = args[2]
            
            if args[5]:
                params['order_detail_no'] = args[5]
            
            if args[6]:
                params['user_name'] = args[6]
            
            if args[7]:
                params['phone'] = args[7]
            
            if args[8]:
                params['seller_name'] = args[8]
            
            if args[9]:
                params['product_name'] = args[9]

            conn = get_connection()
            if conn:
                result = self.service.get_order_list(conn, params)
            
            return jsonify(result), 200
        
        finally:
            conn.close()
    
    # order status type 변경
    # @login_required
    def patch(self):
        conn = None
        try:
            data = request.data
            conn = get_connection()
            if conn:
                self.service.patch_order_status_type(conn, data)
            
            conn.commit()
            
            return jsonify(''), 200
        
        finally:
            conn.close()