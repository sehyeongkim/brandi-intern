'''
    dev_error_message : 개발자 에러 메시지
    error_message : 사용자 에러 메시지
'''

from flask import jsonify

class CustomUserError(Exception):
    def __init__(self, status_code, dev_error_message, error_message):
        self.status_code = status_code
        self.dev_error_message = dev_error_message
        self.error_message = error_message

class DatabaseCloseFail(CustomUserError):
    def __init__(self, error_message):
        status_code = 500
        dev_error_message = "database.close() error"
        super().__init__(status_code, dev_error_message, error_message)

class DatabaseConnectFail(CustomUserError):
    def __init__(self,error_message):
        status_code = 500
        dev_error_message = "database.connect error"
        super().__init__(status_code, dev_error_message, error_message)

class TokenIsEmptyError(CustomUserError):
    def __init__(self, error_message):
        status_code = 400
        dev_error_message = "token is empty"
        super().__init__(status_code, dev_error_message, error_message)

class UserNotFoundError(CustomUserError):
    def __init__(self, error_message):
        status_code = 404
        dev_error_message = "user not found"
        super().__init__(status_code, dev_error_message, error_message)

class JwtInvalidSignatureError(CustomUserError):
    def __init__(self, error_message):
        status_code = 500
        dev_error_message = "signature is damaged"
        super().__init__(status_code, dev_error_message, error_message)

class JwtDecodeError(CustomUserError):
    def __init__(self, error_message):
        status_code = 500
        dev_error_message = "token is damaged"
        super().__init__(status_code, dev_error_message, error_message)