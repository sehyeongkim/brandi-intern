from model import AccountDao

class AccountService:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.account_dao = AccountDao()

    # account 회원가입
    def post_account_signup(self, conn, body):
        return account_dao.post_account_signup(conn, body)
    
    # seller or master 로그인
    def post_account_login(self, conn, body):
        return account_dao.post_seller_login(conn, body)