'''
    dev_error_message : 개발자 에러 메시지
    error_message : 사용자 에러 메시지
    
    class errorClassName(CustomUserError):
        # parameter 설명
        # 두 번째 인자 : user error message 세 번째 인자 : dev error message 
        def __init__(self, error_message, dev_error_message):
            status_code = 500  # 에러코드
            if not dev_error_message :
                dev_error_message = "default error message"
            super().__init__(status_code, dev_error_message, error_message)
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
        
class SignUpFail(CustomUserError):
    def __init__(self, error_message, dev_error_message=None):
        status_code = 400
        if not dev_error_message:
            dev_error_message = "SignUpFail error"
        super().__init__(status_code, dev_error_message, error_message)
    
class SignInError(CustomUserError):
    def __init__(self, error_message, dev_error_message=None):
        status_code = 400
        if not dev_error_message:
            dev_error_message = "SignInFaill error"
        super().__init__(status_code, dev_error_message, error_message)
        
class TokenCreateError(CustomUserError):
    def __init__(self, error_message, dev_error_message=None):
        status_code = 400
        if not dev_error_message:
            dev_error_message = "TokenCreate error"
    
class StartDateFail(CustomUserError):
    def __init__(self,error_message):
        status_code = 400
        dev_error_message = "start_date gt end_date error"
        super().__init__(status_code, dev_error_message, error_message)