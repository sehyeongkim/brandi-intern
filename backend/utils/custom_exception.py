'''
    dev_error_message : 개발자 에러 메시지
    error_message : 사용자 에러 메시지
'''

from flask import jsonify
from flask_request_validator import AbstractRule
from flask_request_validator.exceptions import RuleError, RequiredJsonKeyError, RequestError

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
    
class StartDateFail(CustomUserError):
    def __init__(self,error_message):
        status_code = 400
        dev_error_message = "start_date gt end_date error"
        super().__init__(status_code, dev_error_message, error_message)

class IsInt(AbstractRule):
    def validate(self, value):
        if not isinstance(value, int):
            raise RuleError('invalid request')
        return value

class IsStr(AbstractRule):
    def validate(self, value):
        if not isinstance(value, str):
            raise RuleError('invalid request')
        return value

class IsFloat(AbstractRule):
    def validate(self, value):
        if not isinstance(value, float):
            raise RuleError('invalid request')
        return value

class IsRequired(AbstractRule):
    def validate(self, value):
        if not value:
            raise RuleError('invalid request')
        return value