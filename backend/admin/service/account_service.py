class AccountService:
    def __init__(self, account_dao):
        self.account_dao = account_dao
    
    # account 회원가입
    def post_account_signup(self, conn, data):
        return self.account_dao.post_account_signup(conn, data)
    
    # seller or master 로그인
    def post_account_login(self, conn, data):
        return self.account_dao.post_seller_login(conn, data)