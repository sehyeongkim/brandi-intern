from flask import jsonify

from flask_request_validator import *
from flask_request_validator.error_formatter import demo_error_formatter
from flask_request_validator.exceptions import InvalidRequestError, InvalidHeadersError, RuleError
from utils.custom_exception import CustomUserError
from utils.response import error_response

from pymysql import err
import traceback


def error_handle(app):
    @app.errorhandler(Exception)
    def handle_error(e):
        pass

    @app.errorhandler(AttributeError)
    def handle_error(e):
        traceback.print_exc()
        return error_response("서버 상에서 오류가 발생했습니다.", "NoneType Error", 500)

    @app.errorhandler(KeyError)
    def handle_key_error(e):
        traceback.print_exc()
        return error_response("데이터베이스에서 값을 가져오는데 문제가 발생하였습니다.", "Database Key Error", 500)

    @app.errorhandler(TypeError)
    def handle_type_error(e):
        traceback.print_exc()
        return error_response("데이터의 값이 잘못 입력되었습니다", "Data Type Error", 500)
 
    @app.errorhandler(ValueError)
    def handle_value_error(e):
        traceback.print_exc()
        return error_response("데이터에 잘못된 값이 입력되었습니다.", "Data Value Error", 500)
    
    # @app.errorhandler(err.OperationalError)
    # def handle_operational_error(e):
    #     traceback.print_exc()
    #     return error_response(e, "에러")

    @app.errorhandler(InvalidRequestError)
    def data_error(e):
        dev_error_message = demo_error_formatter(e)[0]['errors'] , "  " , demo_error_formatter(e)[0]['message']
        return error_response("부적절한 값 요청", dev_error_message, 400)
    
    @app.errorhandler(CustomUserError)
    def handle_error(e):
        return error_response(e.error_message, e.dev_error_message, e.status_code)
    
    