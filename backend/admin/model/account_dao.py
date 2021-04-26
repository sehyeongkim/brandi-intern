import pymysql

class AccountDao:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def get_userid(self, conn, data):
        """id 중복확인 함수
        
        Args:
            conn (class): DB 클래스
            data (dict): BODY에서 넘어온 seller 회원가입 정보
        """
        sql_select = """
            SELECT
                *
            FROM
                sellers
            WHERE
                seller_identification = %(id)s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql_select, data)
            return cursor.fetchall()
        
    def get_korean_brand_name(self, conn, data):
        """한글 브랜드 이름 중복확인 함수

        Args:
            conn (class): DB 클래스
            data (dict): BODY에서 넘어온 seller 회원가입 정보
        """
        sql_select = """
            SELECT
                korean_brand_name
            FROM
                sellers
            WHERE
                korean_brand_name = %(korean_brand_name)s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql_select, data)
            return cursor.fetchall()
        
    def get_english_brand_name(self, conn, data):
        """영어 브랜드 이름 중복확인 함수

        Args:
            conn (class): DB 클래스
            data (dict): BODY에서 넘어온 seller 회원가입 정보
        """
        sql_select = """
            SELECT
                english_brand_name
            FROM
                sellers
            WHERE
                english_brand_name = %(english_brand_name)s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql_select, data)
            return cursor.fetchall()
        
    def get_property_id(self, conn, data):
        """property_id 가져오는 함수
        
        sub_property_id를 이용해서 property_id를 구하는 함수
        
        Args:
            conn (class): DB 클래스
            data (dict): BODY에서 넘어온 seller 회원가입 정보
        """
        sql_select = """
            SELECT
                property_id 
            FROM
                sub_property
            WHERE
                id = %(sub_property_id)s limit 1
        """
        with conn.cursor() as cursor:
            cursor.execute(sql_select, data)
            return cursor.fetchone()
    
    def create_account(self, conn, data):
        """account 생성하는 함수
        
        account 함수 생성 후 id 반환

        Args:
            conn (class): DB 클래스 
            data (dict): BODY에서 넘어온 seller 회원가입 정보
        """  
        sql_insert = """
            INSERT INTO account ( 
                account_type_id
            )
            VALUES (
                %(account_type_id)s
            )
        """
        with conn.cursor() as cursor:
            cursor.execute(sql_insert, data)
            return cursor.lastrowid
    
    def create_managers_history(self, conn, data):
        """account history 생성하는 함수

        Args:
            conn (class): DB 클래스
            data (dict): BODY에서 넘어온 seller 회원가입 정보
        """
        sql_insert = """
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
            cursor.execute(sql_insert, data)
            return cursor.lastrowid
        
    def create_seller_signup(self, conn, data):
        """seller 생성하는 함수
            
        Args:
            conn (class): DB 클래스
            data (dict]): BODY에서 넘어온 seller 회원가입 정보
        """
        sql_insert = """
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
            cursor.execute(sql_insert, data)
            return cursor.lastrowid

    def create_manager(self, conn, data):
        """manager 테이블에 seller 정보 입력
        Args:
            conn (class): DB 클래스
            data (dict): BODY에서 넘어온 seller 회원가입 정보
        """
        sql_insert = """
            INSERT INTO managers (
                seller_id,
                phone
            ) VALUES (
                %(seller_id)s,
                %(phone)s
            )
        """
        with conn.cursor() as cursor:
            cursor.execute(sql_insert, data)
            return cursor.lastrowid
    
    def create_seller_history(self, conn, data):
        """seller history 생성하는 함수
        
        Args:
            conn (class): DB 클래스
            data (dict): BODY에서 넘어온 seller 회원가입 정보
        """
        sql_insert = """
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
            cursor.execute(sql_insert, data)
            return cursor.lastrowid
    
    def post_account_login(self, conn, data):
        """seller, master 로그인 하는 함수

        Args:
            conn (class): DB 클래스
            data ([type]): BODY에서 넘어온 seller, master 로그인 정보
        """
        sql_select = """
            SELECT 
                seller_identification, password, is_deleted, account_id
            FROM 
                sellers
            WHERE 
                is_deleted = 0
                AND seller_identification = %(id)s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql_select, data)
            return cursor.fetchone()

    # decorator 가 account_id 비교하는 로직
    def decorator_find_account(self, conn, account_id: int):
        with conn.cursor() as cursor:
            sql = """
                    SELECT
                    *
                    FROM
                    account
                    WHERE
                    id = :account_id
                """
            cursor.execute(sql)
            return cursor.fetchone()