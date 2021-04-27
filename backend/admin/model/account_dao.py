
import pymysql

class AccountDao:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def get_userid(self, conn, params):
        """id 중복확인 함수
        
        Args:
            conn (class): DB 클래스
            params (dict): BODY에서 넘어온 seller 회원가입 정보
        """
        sql = """
            SELECT
                *
            FROM
                sellers
            WHERE
                seller_identification = %(id)s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    def get_account_type_id(self, conn, params):
        """account_type_id를 가져오는 함수

        Args:
            conn (class): DB 클래스
            params (dict): seller id값을 이용해서 가져온 seller_info 정보
        """
        sql = """
            SELECT
                account_type_id
            FROM
                account
            WHERE
                id = %(account_id)s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
        
    def get_korean_brand_name(self, conn, params):
        """한글 브랜드 이름 중복확인 함수

        Args:
            conn (class): DB 클래스
            params (dict): BODY에서 넘어온 seller 회원가입 정보
        """
        sql = """
            SELECT
                korean_brand_name
            FROM
                sellers
            WHERE
                korean_brand_name = %(korean_brand_name)s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
        
    def get_english_brand_name(self, conn, params):
        """영어 브랜드 이름 중복확인 함수

        Args:
            conn (class): DB 클래스
            params (dict): BODY에서 넘어온 seller 회원가입 정보
        """
        sql = """
            SELECT
                english_brand_name
            FROM
                sellers
            WHERE
                english_brand_name = %(english_brand_name)s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
        
    def get_property_id(self, conn, params):
        """property_id 가져오는 함수
        
        sub_property_id를 이용해서 property_id를 구하는 함수
        
        Args:
            conn (class): DB 클래스
            params (dict): BODY에서 넘어온 seller 회원가입 정보
        """
        sql = """
            SELECT
                property_id 
            FROM
                sub_property
            WHERE
                id = %(sub_property_id)s limit 1
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
    
    def create_account(self, conn, params):
        """account 생성하는 함수
        
        account 함수 생성 후 id 반환

        Args:
            conn (class): DB 클래스 
            params (dict): BODY에서 넘어온 seller 회원가입 정보
        """  
        sql = """
            INSERT INTO account ( 
                account_type_id
            )
            VALUES (
                %(account_type_id)s
            )
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.lastrowid
    
    def create_managers_history(self, conn, params):
        """account history 생성하는 함수

        Args:
            conn (class): DB 클래스
            params (dict): BODY에서 넘어온 seller 회원가입 정보
        """
        sql = """
            INSERT INTO managers_history (
                manager_id,
                phone
            )
            VALUES (
                %(managers_id)s,
                %(phone)s
            )
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.lastrowid
        
    def create_seller_signup(self, conn, params):
        """seller 생성하는 함수
            
        Args:
            conn (class): DB 클래스
            params (dict]): BODY에서 넘어온 seller 회원가입 정보
        """
        sql = """
            INSERT INTO sellers (
                property_id,
                sub_property_id,
                account_id,
                seller_identification,
                password,
                korean_brand_name,
                english_brand_name,
                customer_center_number
            ) 
            VALUES (
                %(property_id)s,
                %(sub_property_id)s,
                %(account_id)s,
                %(id)s,
                %(password)s,
                %(korean_brand_name)s,
                %(english_brand_name)s,
                %(customer_center_number)s
            )
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.lastrowid

    def create_manager(self, conn, params):
        """manager 테이블에 seller 정보 입력
        Args:
            conn (class): DB 클래스
            params (dict): BODY에서 넘어온 seller 회원가입 정보
        """
        sql = """
            INSERT INTO managers (
                seller_id,
                phone
            ) VALUES (
                %(seller_id)s,
                %(phone)s
            )
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.lastrowid
    
    def create_seller_history(self, conn, params):
        """seller history 생성하는 함수
        
        Args:
            conn (class): DB 클래스
            params (dict): BODY에서 넘어온 seller 회원가입 정보
        """
        sql = """
            INSERT INTO sellers_history (
                seller_id,
                property_id,
                sub_property_id,
                korean_brand_name,
                english_brand_name,
                customer_center_number
            ) VALUES (
                %(seller_id)s,
                %(property_id)s,
                %(sub_property_id)s,
                %(korean_brand_name)s,
                %(english_brand_name)s,
                %(customer_center_number)s
            )
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.lastrowid
    
    def post_account_login(self, conn, params):
        """seller 로그인

        Args:
            conn (class): DB 클래스
            params ([type]): BODY에서 넘어온 seller 정보
        """
        sql = """
            SELECT 
                seller_identification, password, is_deleted, account_id
            FROM 
                sellers
            WHERE 
                is_deleted = 0
                AND seller_identification = %(id)s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()

    def post_master_login(self, conn, params):
        """master 로그인

        Args:
            conn (class): DB 클래스
            params ([type]): BODY에서 넘어온 master 정보
        """
        sql = """
            SELECT
                email, password, is_deleted, account_id
            FROM
                master
            WHERE
                is_deleted = 0
                AND email = %(id)s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
        
    # decorator 가 account_id 비교하는 로직
    def decorator_find_account(self, conn, account_id: int):
        sql = """
            SELECT
                a.id,
                a.account_type_id
            FROM
                account AS a
            WHERE
                a.id = %(account_id)s
        """
        params = dict()
        params['account_id'] = account_id
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
