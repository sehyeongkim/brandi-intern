import jwt

from flask import g, request, jsonify
from functools import wraps

from config import SECRET_KEY
from connection import get_connection

from admin.model import AccountDao

from utils.custom_exception import (
                                    TokenIsEmptyError, 
                                    UserNotFoundError, 
                                    DatabaseConnectFail, 
                                    DatabaseCloseFail, 
                                    JwtInvalidSignatureError,
                                    JwtDecodeError
)


def login_required(f):
    @wraps(f)
    def decorated_function(self, *args, **kwargs):
        conn = None
        try:
            token = request.headers.get('Authorization')
            if not token:
                raise TokenIsEmptyError('토큰이 존재하지 않습니다.')
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            account_id = payload['account_id']

            conn = get_connection()
            if not conn:
                raise DatabaseConnectFail('서버와 연결이 불가능합니다.')

            result = AccountDao().decorator_find_account(conn, account_id)
            if not account:
                raise UserNotFoundError('존재하지 않는 사용자입니다.')
            
            g.account_id = result['id']
            g.account_type_id = result['account_type_id']
            
            return f(self, *args, **kwargs)
        
        except jwt.exceptions.InvalidSignatureError:
            raise JwtInvalidSignatureError('토큰이 손상되었습니다.')
        
        except jwt.exceptions.DecodeError:
            raise JwtDecodeError('토큰이 손상되었습니다.')
        
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    raise DatabaseCloseFail('서버와 연결을 종료하는 중 에러가 발생했습니다.')

    return decorated_function