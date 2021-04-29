from flask.views import MethodView
from flask import request, jsonify
from flask_request_validator import Param, Pattern, JSON, validate_params, ValidRequest
from flask_request_validator.error_formatter import demo_error_formatter
from flask_request_validator.exceptions import InvalidRequestError, InvalidHeadersError, RuleError


from utils.custom_exception import DatabaseCloseFail
from utils.response import post_response

from connection import get_connection


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
        Param('id', JSON, str, rules=[Pattern("^[a-z]+[a-z0-9]{4,19}$")], required=True),
        Param('password', JSON, str, rules=[Pattern('^[A-Za-z0-9@#$]{6,12}$')], required=True)
    )
    def post(self, valid):
        conn = None
        try:
            body = valid.get_json()
            conn = get_connection()
            if conn:
                result = self.service.post_account_login(conn, body)

            return post_response({
                        "message" : "success", 
                        "accessToken" : result['accessToken'], 
                        "account_id" : result['account_id'],
                        "status_code" : 200
                        })

        finally:
            try:
                conn.close()
            except Exception as e:
                raise DatabaseCloseFail('서버에 알 수 없는 오류가 발생했습니다.')