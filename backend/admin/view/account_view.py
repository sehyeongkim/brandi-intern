from flask.views import MethodView

from connection import get_connection

class AccountSignUpView(MethodView):
    def __init__(self, service):
        self.service = service
    
    # account 회원가입
    def post(self):
        conn = None
        try:
            data = request.data
            conn = get_connection()
            if conn:
                self.service.post_account_signup(conn, data)
            
            conn.commit()
            
            return jsonify(''), 200

        finally:
            conn.close()


class AccountLogInView(MethodView):
    def __init__(self, service):
        self.service = service
    
    # seller or master 로그인
    def post(self):
        conn = None
        try:
            data = request.data
            conn = get_connection()
            if conn:
                result = self.service.post_account_login(conn, data)
            
            conn.commit()

            return jsonify('access_token'), 200

        finally:
            conn.close()