from utils.response import error_response, get_response, post_response, post_response_with_return
from flask import request, jsonify, g
from flask.views import MethodView
from flask_request_validator import validate_params, Param, GET, ValidRequest, JsonParam, Min, Enum, Datetime
from connection import get_connection
from utils.response import error_response, get_response, post_response, post_response_with_return
from utils.custom_exception import DataNotExists, StartDateFail
from utils.decorator import LoginRequired

from utils.custom_exception import DataNotExists, StartDateFail

class OrderListView(MethodView):
    def __init__(self, service):
        self.service = service
    
    # 주문 조회
    @LoginRequired("seller")
    @validate_params(
        Param('start_date', GET, str, rules=[Datetime('%Y-%m-%d')], required=True),
        Param('end_date', GET, str, rules=[Datetime('%Y-%m-%d')], required=True),
        Param('sub_property_id', GET, int, required=False),
        Param('order_number', GET, str, required=False),
        Param('order_status_type_id', GET, int, required=True),
        Param('order_detail_number', GET, str, required=False),
        Param('order_username', GET, str, required=False),
        Param('orderer_phone', GET, str, required=False),
        Param('seller_name', GET, str, required=False),
        Param('product_name', GET, str, required=False),
        Param('page', GET, int, required=False, default=1, rules=[Min(1)]),
        Param('limit', GET, int, required=False, default=10, rules=[Enum(10, 20, 50)])
    )
    def get(self, valid):
        """주문 조회 리스트

        어드민 페이지의 주문관리 페이지에서 필터 조건에 맞는 주문 리스트 출력

        Args:
            valid (ValidRequest): validate_params 데코레이터로 전달된 값
            
        Returns:
            order_list_result (dict): 결제일자, 주문번호, 주문상세번호, 상품명, 주문상태 등 주문 조회 리스트 관련 정보
            200: 주문 조회 리스트 가져오기 성공
            500: Exception
                KeyError - query parameter로 잘못된 key값이 들어올 경우에 발생하는 에러
        """
        conn = None
        try:
            params = valid.get_params()
            conn = get_connection()   
            
            order_list_result = self.service.get_order_list(conn, params)
         
            return get_response(order_list_result), 200
        
        finally:
            conn.close()
    
    # order_status_type 변경
    # LoginRequired의 경우 user가 아닌 경우를 구별하기 위함이므로 master도 포함일 때는 seller로 작성해도 무관
    @LoginRequired("seller")
    def patch(self):
        """주문 및 배송처리 

        주문 상태를 관리한다. 예를 들어, 상품 준비에서 배송중, 배송중에서 배송완료 등으로 주문의 현재 상태를 수정해준다.

        Returns:
            "SUCCESS" (dict) : 성공했을 때, Success 메시지를 반환 
            not_possible_change_values (dict) : 일부 값 변경에 실패할 경우 실패한 값을 반환
        """
        conn = None
        try:
            params = request.get_json()
            conn = get_connection()
            
            # 주문 상태 변경 요청 중 바꿀 수 없는 값을 반환 (구매확정, 환불완료 등은 수정할 수 없다.)
            not_possible_change_values = self.service.patch_order_status_type(conn, params)
            conn.commit()
              
            return post_response_with_return("SUCCESS", not_possible_change_values), 200
        except Exception as e:
            if conn:
                # 수정 중 문제가 발생할 경우 transaction을 적용
                conn.rollback()
            raise e
        finally:
            try:
                conn.close()
            except Exception as e:
                raise DatabaseCloseFail('서버에 알 수 없는 오류가 발생했습니다.')


class OrderView(MethodView):
    def __init__(self, service):
        self.service = service 

    @LoginRequired("seller")
    def get(self, order_detail_number):
        """주문 상세 뷰

        어드민 페이지의 주문관리 페이지에서 주문상세번호를 클릭했을 때, 주문 상세 정보를 출력

        Args:
            valid (ValidRequest): validate_params 데코레이터로 전달된 값 
            
        Returns:
            order_detail (dict): 주문정보, 주문상세정보, 상품정보, 수취자정보, 주문상태 이력변경 등의 정보
            200: 주문 상세 정보 가져오기 성공
            500: Exception
        """
        conn = None
        try:
            params = dict()
            params["detail_order_number"] = order_detail_number
            conn = get_connection()

            order_detail = self.service.get_order(conn, params)
            return get_response(order_detail), 200
        
        finally:
            conn.close()

class DashboardSellerView(MethodView):
    def __init__(self, service):
        self.service = service
    
    @LoginRequired('seller')
    def get(self):
        """Seller Dashboard Page
     
        Seller 로그인 시 상품,판매 현황 출력
            
        Returns:
            dict: 전체상품, 판매중상품, 배송준비중, 배송완료, 결제건수(30일간), 결제금액(30일간)
            200: 현황 정보 가져오기 성공
            500: Exception
        """
        account_id = g.account_id
        conn = None
        try:
            conn = get_connection()
            result = self.service.get_dashboard_seller(conn, account_id)
            return get_response(result, 200)        
        finally:
            try:
                conn.close()
            except Exception as e:
                raise DatabaseCloseFail('서버에 알 수 없는 오류가 발생했습니다.')
