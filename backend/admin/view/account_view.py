from flask.views import MethodView
from flask import request, jsonify
from flask_request_validator import Param, Pattern, JSON, validate_params, ValidRequest
from flask_request_validator.error_formatter import demo_error_formatter
from flask_request_validator.exceptions import InvalidRequestError, InvalidHeadersError, RuleError

from utils.custom_exception import DatabaseCloseFail
from utils.response import post_response

from connection import get_connection
from utils.decorator import LoginRequired



class AccountSignUpView(MethodView):
    def __init__(self, service):
        self.service = service
    # account 회원가입
    # router => class => validate_params
    # rules 최상단에서 에러 처리
    # 최종적인 메시지 처리는 최상단에서
    # 어떤 문제가 있는지 멘트 처리 알아보기

    @validate_params(
        Param('id', JSON, str, rules=[
              Pattern("^[a-z]+[a-z0-9]{4,19}$")], required=True),
        Param('password', JSON, str, rules=[
              Pattern('^[A-Za-z0-9@#!$]{6,12}$')], required=True),
        Param('phone', JSON, str, required=True),
        Param('sub_property_id', JSON, int, required=True),
        Param('korean_brand_name', JSON, str, required=True,
              rules=[Pattern('[가-힣a-zA-Z0-9]+')]),
        Param('english_brand_name', JSON, str, required=True,
              rules=[Pattern('[a-zA-Z0-9]+')]),
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
                raise DatabaseCloseFail('서버에 알 수 없는 오류가 발생했습니다')


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
            if body['id'].find("@") == -1 :
                # Seller 로그인
                result = self.service.post_account_login(conn, body)
            else:
                # Master 로그인
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