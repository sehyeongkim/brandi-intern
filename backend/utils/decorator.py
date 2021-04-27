import jwt

from flask import g, request
from functools import wraps


from config import SECRET_KEY
from connection import get_connection

from admin.model import AccountDao

from utils.custom_exception import (
    TokenIsEmptyError,
    UserNotFoundError,
    DatabaseCloseFail,
    JwtInvalidSignatureError,
    JwtDecodeError,
    MasterLoginRequired,
    SellerLoginRequired
)


class LoginRequired:
    """ Login Decorator

        login decorator에서 account_type을 argument로 받아서
        seller, master, user의 권한이 필요한 경우를 처리
        
        계정과 권한이 맞으면 g 객체에 account_id와 account_type을 담음
    """
    def __init__(self, *a, **kw):
        if len(a) > 0:
            self.account_type = a[0]
        else:
            self.account_type = 'user'

    def __call__(self, func):
        @wraps(func)
        def wrapper(target, *args, **kwargs):
            conn = None
            try:
                token = request.headers.get('Authorization')
                if not token:
                    raise TokenIsEmptyError('토큰이 존재하지 않습니다.')

                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                account_id = payload['account_id']

                conn = get_connection()
                
                result = AccountDao().decorator_find_account(conn, account_id)
                if not result:
                    raise UserNotFoundError('존재하지 않는 사용자입니다.')

                # account_type_id = 1은 master. master의 권한이 필요한데 account_type이 master가 아닌 경우 error raise
                if self.account_type == 'master' and result['account_type_id'] != 1:
                    raise MasterLoginRequired('마스터 계정 로그인이 필요합니다.')

                # account_type_id = 3은 user. seller 이상의 권한이 필요한데 account_type이 user일 때 error raise
                if self.account_type == 'seller' and result['account_type_id'] == 3:
                    raise SellerLoginRequired('판매자 또는 마스터 계정 로그인이 필요합니다.')

                g.account_id = result['id']
                g.account_type_id = result['account_type_id']

                return func(target, *args, **kwargs)

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

        return wrapper