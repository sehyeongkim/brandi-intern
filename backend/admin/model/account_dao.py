
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

    # id도 함께 날려준다.
    def get_seller_status(self, conn, seller_status_type):
        sql = """
            SELECT
                st.name AS status_name,
                stb.seller_status_type_id,
                stb.seller_status_button_id,
                sb.name as button_name,
                sb.to_status_type_id AS to_status_type_id
            FROM
                seller_status_type_button AS stb
            right outer JOIN
                seller_status_type AS st 
                on st.id = stb.seller_status_type_id
            left outer JOIN
                seller_status_button As sb
                on sb.id = stb.seller_status_button_id
            WHERE
                st.name = %(seller_status_type)s
            ORDER BY st.id ASC;
        """

        with conn.cursor() as cursor:
            cursor.execute(sql, {"seller_status_type":seller_status_type})
            result = cursor.fetchall()
            return result

    def get_seller_list(self, conn, params):
        select = """
            SELECT 
        """

        seller_info = """
                sst.id AS seller_status_type_id,
                s.id as seller_id, 
                s.seller_identification, 
                s.english_brand_name, 
                s.korean_brand_name, 
                m.name as manager_name, 
                sst.name as seller_status_type, 
                m.phone as manager_phone, 
                m.email as manager_email, 
                sb.name as sub_property, 
                DATE_FORMAT(s.created_at, '%%Y-%%m-%%d %%h:%%i:%%s') as seller_created_date
        """

        condition = """
            FROM 
                sellers as s
            INNER JOIN
                managers as m ON s.id = m.seller_id
            INNER JOIN
                sub_property as sb ON s.sub_property_id = sb.id
            INNER JOIN
                seller_status_type as sst ON sst.id = s.seller_status_type_id
            WHERE
                    s.created_at BETWEEN '0000-00-00 00:00:00' AND '9999-12-30 00:00:00'
        """

        sql_1 = select + seller_info + condition

        if 'id' in params:
            condition += """
                AND
                    s.id = %(id)s
            """
        
        # 이 부분은 직접 확인해보고 수정
        if 'seller_identification' in params:
            condition += """
                AND 
                    s.seller_identification LIKE %(seller_identification)s 
            """

        if 'english_brand_name' in params:
            condition += """
                AND
                    s.english_brand_name LIKE %(english_brand_name)s
            """
        
        if 'korean_brand_name' in params:
            condition += """
                AND
                    s.korean_brand_name LIKE %(korean_brand_name)s
            """
        
        if 'manager_name' in params:
            condition += """
                AND
                    m.name LIKE %(manager_name)s
            """
        
        if 'seller_status_type' in params:
            condition += """
                AND
                    s.seller_status_type_id = %(seller_status_type_id)s
            """
        
        if 'manager_phone' in params:
            condition += """
                AND
                    m.phone LIKE %(manager_phone)s
            """
        
        if 'sub_property_id' in params:
            condition += """
                AND
                    s.sub_property_id = %(sub_property_id)s
            """
        
        if 'start_date' in params and 'end_date' in params:
            condition += """
                AND
                    s.created_at BETWEEN %(start_date)s AND %(end_date)s
            """
        
        limit = """
                LIMIT
                    %(limit)s
                OFFSET
                    %(page)s
        """

        count = """
                COUNT(*) as count 
        """

        sql_select_seller_info = select + seller_info + condition + limit
        sql_select_seller_count = select + count + condition + limit
        with conn.cursor() as cursor:
            cursor.execute(sql_select_seller_info, params)
            seller_info_list = cursor.fetchall()

            cursor.execute(sql_select_seller_count, params)
            seller_counts = cursor.fetchone()

            return seller_info_list, seller_counts