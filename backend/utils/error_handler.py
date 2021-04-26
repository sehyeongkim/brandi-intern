from flask import jsonify

from flask_request_validator import *
from flask_request_validator.error_formatter import demo_error_formatter
from flask_request_validator.exceptions import InvalidRequestError, InvalidHeadersError, RuleError
from utils.custom_exception import CustomUserError
from utils.response import error_response

def error_handle(app):
    """에러 핸들러
    
    에러 처리하는 함수
    
    Args:
        app ([type]): __init__.py에서 파라미터로 app을 전달 받은 값
    Returns:
        json : error_response() 함수로 에러 메시지를 전달해서 반환 받고 return
    """
    @app.errorhandler(Exception)
    def handle_error(e):
        pass
    
    @app.errorhandler(InvalidRequestError)
    def data_error(e):
        """validate_params 정규식 에러
        validate_params rules에 위배될 경우 발생되는 에러 메시지를 처리하는 함수
        """
        dev_error_message = demo_error_formatter(e)[0]['errors'] , demo_error_formatter(e)[0]['message']
        return error_response("형식에 맞는 값을 입력해주세요", dev_error_message, 400)
    
    @app.errorhandler(CustomUserError)
    def handle_error(e):
        return error_response(e.error_message, e.dev_error_message, e.status_code)
    