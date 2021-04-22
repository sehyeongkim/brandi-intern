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
    def get(self, valid):
        """주문 조회 리스트 뷰

        어드민 페이지의 주문관리 페이지에서 필터 조건에 맞는 주문 리스트 출력

        Args:
            valid (ValidRequest): validate_params 데코레이터로 전달된 값
            
        Returns:
            get_response(order_list_result): 결제일자, 주문번호, 주문상세번호, 상품명, 주문상태 등 주문 조회 리스트 관련 정보
            200: 주문 조회 리스트 가져오기 성공

            500: Exception
        """
        conn = None
        try:
            params = valid.get_params()
            conn = get_connection()
<<<<<<< HEAD

            order_list_result = self.service.get_order_list(conn, params)
            return jsonify(order_list_result), 200
=======
            if conn:
                order_list_result = self.service.get_order_list(conn, params)
            # return jsonify(order_list_result), 200
            return post_response(order_list_result), 200
>>>>>>> admin
        
        finally:
            conn.close()
    
    # order_status_type 변경
    # @login_required
    # @validate_params(
    #     Param('')
    # )
    def patch(self):
        conn = None
        try:
            body = request.get_json()
<<<<<<< HEAD
            conn = get_connection()

            self.service.patch_order_status_type(conn, body)
            conn.commit()
            
            return jsonify({"message" : "SUCCESS"}), 200
        
        finally:
            conn.close()


class OrderView(MethodView):
    def __init__(self, service):
        self.service = service    
    
    @validate_params(
        Param('detail_order_number', GET, str, required=True)
    )
    def get(self, valid: ValidRequest):
        """주문 상세 뷰

        어드민 페이지의 주문관리 페이지에서 주문상세번호를 클릭했을 때, 주문 상세 정보를 출력

        Args:
            valid (ValidRequest): validate_params 데코레이터로 전달된 값 
            
        Returns:
            get_response(order_detail): 주문정보, 주문상세정보, 상품정보, 수취자정보, 주문상태 이력변경 등의 정보
            200: 주문 상세 정보 가져오기 성공

            500: Exception
        """
        conn = None
        try:
            params = valid.get_params()
            conn = get_connection()

            order_detail = self.service.get_order(conn, params)
            return jsonify(order_detail), 200
=======
            
            conn = get_connection()
                
            self.service.patch_order_status_type(conn, body)
                        
            conn.commit()
            
            # return jsonify({"message" : "SUCCESS"}), 200
            return get_response("SUCCESS"), 200
>>>>>>> admin
        
        finally:
            conn.close()



    def get(self, request):
        user_id = request.user
        