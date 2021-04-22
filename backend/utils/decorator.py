# decorator
import jwt

from flask import g, request
from functools import wraps

from connection import get_connection

from admin.model import AccountDao

def login_required(f):
    @wraps(f)
    def decorated_function(self, *args, **kwargs):
        conn = None
        try:

            token = request.headers.get('Authorization')
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            account_id = payload['account_id']

            conn = get_connection()
            if conn:
                result = AccountDao().decorator_find_account(conn, account_id)
            
            return f(*args, **kwargs)

        finally:
            conn.close()

    return decorated_function