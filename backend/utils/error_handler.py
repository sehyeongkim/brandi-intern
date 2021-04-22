from flask import jsonify
from flask_request_validator.exceptions import InvalidRequestError

from flask_request_validator import *
from flask_request_validator.error_formatter import demo_error_formatter
from flask_request_validator.exceptions import InvalidRequestError, InvalidHeadersError, RuleError
from utils.custom_exception import CustomUserError


from flask import current_app as app

# start error handling
from flask import current_app as app


def error_handle(app):
    @app.errorhandler(Exception)
    def handle_error(e):
        pass
    
    @app.errorhandler(InvalidRequestError)
    def handle_invalid_usage(e):
        return jsonify({'message': e.errors, 'error_message:': ", ".join(e.errors.keys()) + '가(이) 유효하지 않습니다.'}), 400
    
    @app.errorhandler(CustomUserError)
    def handle_error(e):
        return jsonify({"error_message": e.error_message, "dev_error_message": e.dev_error_message, "status" : e.status_code}), e.status_code