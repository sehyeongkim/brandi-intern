import bcrypt, jwt

<<<<<<< HEAD
<<<<<<< HEAD
from admin.model import AccountDao
<<<<<<< HEAD
=======
from model import AccountDao
>>>>>>> Modify: Directory 구조 변경 및 경로 수정정
=======
from admin.model import AccountDao
>>>>>>> Modify: Directory 구조 변경 및 경로 수정 완료
=======
from utils.custom_exception import SignUpFail
>>>>>>> seller 회원가입 기능 구현

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
        checkid = self.account_dao.get_userid(conn, data)
        if checkid:
            raise SignUpFail("중복된 아이디 입니다.", "already_exist_id")
        
        # korean_brand_name 중복확인
        get_korean_brand_name = self.account_dao.get_korean_brand_name(conn, data)
        if get_korean_brand_name:
            raise SignUpFail("중복된 한글 브랜드 이름 입니다.", "already_exist_korean_brand_name")
        
        # english_brand_name 중복확인
        get_english_brand_name = self.account_dao.get_english_brand_name(conn, data)
        if get_english_brand_name:
            raise SignUpFail("중복된 영문 브랜드 이름 입니다.", "already_exist_english_brand_name")
        
        # password hash
        self.set_password_hash(data)
        
        # sub_property_id를 이용해서 property_id값을 가져오기
        get_property_id = self.account_dao.get_property_id(conn, data)
        if not get_property_id:
            raise SignUpFail("카테고리 선택에서 뜻하지 않은 에러가 발생했습니다.","get_property_id error")
        data['property_id'] = get_property_id['property_id']
        
        # account_type (seller = 2)
        data['account_type_id'] = 2
        
        # account 생성
        get_account_id = self.account_dao.create_account(conn, data)
        if not get_account_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "create_account error")
        data['account_id'] = get_account_id
        
        # seller 생성
        get_seller_id = self.account_dao.create_seller_signup(conn, data)
        data['seller_id'] = get_seller_id
        if not get_seller_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "create_seller_signup error")

        # manager 생성 ( seller id를 이용해서 )
        get_managers_id = self.account_dao.create_manager(conn, data)
        if not get_managers_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "crate_manager error")
        data['managers_id'] = get_managers_id
        
        # manager history 생성 ( get_managers_id를 이용해서 )
        get_manager_history_id = self.account_dao.create_managers_history(conn, data)
        if not get_manager_history_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "create_account_history error")
        
        # seller history 생성
        get_sellers_history_id = self.account_dao.create_seller_history(conn, data)
        if not get_sellers_history_id:
            raise SignUpFail("아이디를 생성하는데 오류가 발생했습니다.", "create_seller_history error")

    # seller or master 로그인
    def post_account_login(self, conn, data):
        
        
        return self.account_dao.post_account_login(conn, data)