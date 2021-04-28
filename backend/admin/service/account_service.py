import bcrypt, jwt
from config import SECRET_KEY
from admin.model import AccountDao
from utils.custom_exception import SignUpFail, SignInError, TokenCreateError

class AccountService:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.account_dao = AccountDao()

    def set_password_hash(self, params):
        params['password'] = bcrypt.hashpw(
            params['password'].encode('UTF-8'),
            bcrypt.gensalt()
        ).decode('UTF-8')
        
    def create_token(self, info):
        try:
            token = jwt.encode({"account_id": info['account_id']},
                                SECRET_KEY,
                                algorithm="HS256")
        except Exception as e:
            raise TokenCreateError("뜻하지 않은 에러가 발생했습니다. 다시 시도 해주세요.", "create_token error")
        
        return token
        
    def check_hash_password(self, conn, info, params):
        """ 로그인 hash password 체크하는 함수

        hash password 체크 후 account_type_id, accessToken값을 return하는 함수

        Args:
            conn (class): DB 클래스
            info (dict): post_account_login or post_master_login에서 가져온 계정 정보
            params (dict): BODY에서 넘어온 master or seller 정보

        Returns:
            [dict]: account_type_id , accessToken
        """
        if not info or not bcrypt.checkpw(params['password'].encode('utf-8'), info['password'].encode('utf-8')):
            raise SignInError("정확한 아이디, 비밀번호를 입력해주세요", "post_master_login error")
    
        account_type_id = self.account_dao.get_account_type_id(conn, info)
        token = self.create_token(info)
        return {
            "account_type_id" : account_type_id['account_type_id'],
            "accessToken" : token
        }
    #  ---------------------------------------------------------------------------------------------------------------------
    # account 회원가입
    def post_account_signup(self, conn, params):   
        checkid = self.account_dao.get_userid(conn, params)
        if checkid:
            raise SignUpFail("중복된 아이디 입니다.", "already_exist_id")
        
        # korean_brand_name 중복확인
        get_korean_brand_name = self.account_dao.get_korean_brand_name(conn, params)
        if get_korean_brand_name:
            raise SignUpFail("중복된 한글 브랜드 이름 입니다.", "already_exist_korean_brand_name")
        
        # english_brand_name 중복확인
        get_english_brand_name = self.account_dao.get_english_brand_name(conn, params)
        if get_english_brand_name:
            raise SignUpFail("중복된 영문 브랜드 이름 입니다.", "already_exist_english_brand_name")
        
        # password hash
        self.set_password_hash(params)
        
        # sub_property_id를 이용해서 property_id값을 가져오기
        get_property_id = self.account_dao.get_property_id(conn, params)
        if not get_property_id:
            raise SignUpFail("카테고리 선택에서 뜻하지 않은 에러가 발생했습니다.","get_property_id error")
        params['property_id'] = get_property_id['property_id']
        
        # account_type (seller = 2)
        params['account_type_id'] = 2
        
        # account 생성
        get_account_id = self.account_dao.create_account(conn, params)
        if not get_account_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "create_account error")
        params['account_id'] = get_account_id
        
        # seller 생성
        get_seller_id = self.account_dao.create_seller_signup(conn, params)
        params['seller_id'] = get_seller_id
        if not get_seller_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "create_seller_signup error")
        
        # manager 생성 ( seller id를 이용해서 )
        get_managers_id = self.account_dao.create_manager(conn, params)
        if not get_managers_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "crate_manager error")
        params['managers_id'] = get_managers_id
        
        # manager history 생성 ( get_managers_id를 이용해서 )
        get_manager_history_id = self.account_dao.create_managers_history(conn, params)
        if not get_manager_history_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "create_account_history error")
        
        # seller history 생성
        get_sellers_history_id = self.account_dao.create_seller_history(conn, params)
        if not get_sellers_history_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "create_seller_history error")
        
    # seller 로그인
    def post_account_login(self, conn, params):
        seller_info = self.account_dao.post_account_login(conn, params)
        result = self.check_hash_password(conn, seller_info, params)
        
        return result
    
    # master 로그인
    def post_master_login(self, conn, params):
        master_info = self.account_dao.post_master_login(conn, params)
        result = self.check_hash_password(conn, master_info, params)
        
        return result
