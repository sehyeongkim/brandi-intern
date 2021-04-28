from flask.views import MethodView
from flask import request, jsonify
from flask_request_validator import Param, Pattern, JSON, validate_params, ValidRequest, GET, Min, Enum
from flask_request_validator.error_formatter import demo_error_formatter
from flask_request_validator.exceptions import InvalidRequestError, InvalidHeadersError, RuleError


from utils.custom_exception import DatabaseCloseFail
from utils.response import post_response, get_response

from connection import get_connection

from timeit import repeat

class AccountSignUpView(MethodView):
    def __init__(self, service):
        self.service = service
    
    @validate_params(
        Param('id', JSON, str, rules=[Pattern("^[a-z]+[a-z0-9]{4,19}$")], required=True),
        Param('password', JSON, str, rules=[Pattern('^[A-Za-z0-9@#!$]{6,12}$')], required=True),
        Param('phone', JSON, str, required=True),
        Param('sub_property_id', JSON, int, required=True),
        Param('korean_brand_name', JSON, str, required=True, rules=[Pattern('[가-힣a-zA-Z0-9]+')]),
        Param('english_brand_name', JSON, str, required=True, rules=[Pattern('[a-zA-Z0-9]+')]),
        Param('customer_center_number', JSON, str, required=True)
    )
    def post(self, valid: ValidRequest):
        conn = None
        try:
            body = valid.get_json()
            conn = get_connection()
            self.service.post_account_signup(conn, body)
            conn.commit()

            return post_response({"message": "success", "status_code" : 200}), 200
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            try:
                if conn:
                    conn.close()
            except Exception as e:
                raise DatabaseCloseFail('서버에 알 수 없는 오류가 발생했습니다.')


class AccountLogInView(MethodView):
    def __init__(self, service):
        self.service = service

    
    @validate_params(
        Param('id', JSON, str, rules=[Pattern("^[a-z]+[a-z0-9@.]{4,19}$")], required=True),
        Param('password', JSON, str, rules=[Pattern('^[A-Za-z0-9@#$]{6,12}$')], required=True)
    )
    def post(self, valid):
        conn = None
        try:
            body = valid.get_json()        
            conn = get_connection()
            # 계정을 먼저 가져와서 처리하는게 더 안전
            if body['id'].find("@") == -1:
                print("Seller 로그인")
                result = self.service.post_account_login(conn, body)
            else:
                print("Master 로그인")
                result = self.service.post_master_login(conn, body)
                
            return post_response({
                        "message" : "success", 
                        "accessToken" : result['accessToken'],
                        "account_type_id" : result['account_type_id'],
                        "status_code" : 200
                        }), 200
        finally:
            try:
                conn.close()
            except Exception as e:
                raise DatabaseCloseFail('서버에 알 수 없는 오류가 발생했습니다.')



class SellerListView(MethodView):
    def __init__(self, service):
        self.service=service

    @validate_params(
        Param('id', GET, int, required=False),
        Param('seller_identification', GET, str, required=False),
        Param('english_brand_name', GET, str, required=False),
        Param('korean_brand_name', GET, str, required=False),
        Param('manager_name', GET, str, required=False),
        Param('seller_status_type_id', GET, str, required=False),
        Param('manager_phone', GET, str, required=False),
        Param('manager_email', GET, str, required=False),
        Param('sub_property_id', GET, int, required=False),
        Param('start_date', GET, str, required=False),
        Param('end_date', GET, str, required=False),
        Param('page', GET, int, required=False, default=1, rules=[Min(1)]),
        Param('limit', GET, int, required=False, default=10, rules=[Enum(10, 20, 50)])
    )
    def get(self, valid):
        """셀러 계정 리스트 조회

        Args:
            valid (ValidRequest): parameter로 들어온 값

        Returns:
            seller_list_results (list): 
        """
        conn = None
        try:
            params = valid.get_params()
            conn=get_connection()
            seller_list_results = self.service.get_seller_list(conn, params)

            return get_response(seller_list_results), 200
        finally:
            conn.close()