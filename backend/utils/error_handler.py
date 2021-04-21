from flask import jsonify
from flask_request_validator import *
from flask_request_validator.error_formatter import demo_error_formatter
from flask_request_validator.exceptions import InvalidRequestError, InvalidHeadersError, RuleError
from utils.custom_exception import CustomUserError

# start error handling
from flask import current_app as app


def error_handle(app):
    @app.errorhandler(Exception)
    def handle_error(e):
        pass
    
    @app.errorhandler(InvalidRequestError)
    def data_error(e):
        # customize error messages as you wish
        # Attention! We do not support demo_error_formatter. Demo is just a demo. Feel free to suggest a new formatter
        return jsonify({ 'error_message': format(e)}), 500
    
    @app.errorhandler(CustomUserError)
    def handle_error(e):
        return jsonify({"error_message": e.error_message, "dev_error_message": e.dev_error_message, "status" : e.status_code}), e.status_code
        