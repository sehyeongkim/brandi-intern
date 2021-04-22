import bcrypt, jwt

from admin.model import AccountDao

class AccountService:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.account_dao = AccountDao()

    def set_password_hash(self, data):
        data['password'] = bcrypt.hashpw(
            data['password'].encode('UTF-8'),
            bcrypt.gensalt()
        ).decode('UTF-8')
    #  ---------------------------------------------------------------------------------------------------------------------
    # account 회원가입
    def post_account_signup(self, conn, data):      
        # id 중복검사
        checkid = self.account_dao.get_userid(conn, data['id'])
        if checkid:
            # rasie 방식으로 오류 처리 하도록 (공부)
            return False
        
        # 비밀번호 hash
        self.set_password_hash(data)
        
        # account_type (seller = 2)
        data['account_type_id'] = 2
        
        # account 생성
        self.account_dao.post_account_login(conn, data['account_type_id'])
        
        # seller 생성
        # create_seller_result = self.account_dao.create_seller_signup(conn, data)
        # if not create_seller_result:
            # return False
        
        return self.account_dao.create_seller_signup(conn, data)
    
    # seller or master 로그인
    def post_account_login(self, conn, data):
        return self.account_dao.post_account_login(conn, data)