from flask import jsonify

from flask_request_validator import *
from flask_request_validator.error_formatter import demo_error_formatter
from flask_request_validator.exceptions import InvalidRequestError, InvalidHeadersError, RuleError
from utils.custom_exception import CustomUserError
from utils.response import error_response

def error_handle(app):
    @app.errorhandler(Exception)
    def handle_error(e):
        pass
    
    @app.errorhandler(InvalidRequestError)
    def data_error(e):
        dev_error_message = demo_error_formatter(e)[0]['errors'] , "  " , demo_error_formatter(e)[0]['message']
        return error_response("알 수 없는 오류 발생", dev_error_message, 400)
    
    @app.errorhandler(CustomUserError)
    def handle_error(e):
        return error_response(e.error_message, e.dev_error_message, e.status_code)
    
    