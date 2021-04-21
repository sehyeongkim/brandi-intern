from flask import jsonify
from flask_request_validator.exceptions import InvalidRequestError
# from utils.custom_exceptions import (CustomUserError)


# start error handling
def error_handle(app):
    # pram customized exception
    @app.errorhandler(InvalidRequestError)
    def handle_invalid_usage(e):
        return jsonify({'message': e.errors, 'error_message:': ", ".join(e.errors.keys()) + '가(이) 유효하지 않습니다.'}), 400