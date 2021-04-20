from flask import jsonify
from flask_request_validator.exceptions import InvalidRequestError
# from utils.custom_exceptions import (CustomUserError)


# start error handling
def error_handle(app):
    # pram customized exception
    @app.errorhandler(InvalidRequestError)
    def defhandle_invalid_usage(e):
        print("a실행되냠ㄴㅇ리;ㅓㅁㄴㅇㄹ;ㅣ머;ㅣ럽ㅈㄷ;검ㄴ;ㅣ럼ㄴ;이럼;ㅣㅇ렂;ㅣ겁ㅈ;ㅐㅏ거")
        return jsonify({'message': e.errors, 'error_message:': ", ".join(e.errors.keys()) + '가(이) 유효하지 않습니다.'}), 400