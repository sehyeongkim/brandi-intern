from flask import jsonify
from flask_request_validator.exceptions import InvalidRequestError

from flask_request_validator import *
from flask_request_validator.error_formatter import demo_error_formatter
from flask_request_validator.exceptions import InvalidRequestError, InvalidHeadersError, RuleError
from utils.custom_exception import CustomUserError
from utils.response import error_response

from flask import current_app as app

# start error handling
from flask import current_app as app


def error_handle(app):
    # @app.errorhandler(Exception)
    # def handle_error(e):
    #     return 'good'
    
    @app.errorhandler(InvalidRequestError)
    def data_error(e):
        """validate_params 정규식 에러
        validate_params rules에 위배될 경우 발생되는 에러 메시지를 처리하는 함수
        """
        dev_error_message = demo_error_formatter(e)[0]['errors'] , demo_error_formatter(e)[0]['message']
        return error_response("형식에 맞는 값을 입력해주세요", dev_error_message, 400)

    @app.errorhandler(CustomUserError)
    def handle_error(e):
        return jsonify({"error_message": e.error_message, "dev_error_message": e.dev_error_message, "status" : e.status_code}), e.status_code
    
