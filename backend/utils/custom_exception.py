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