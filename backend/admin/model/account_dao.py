
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
        """ 셀러 계정 상태 가져오는 함수

        셀러 계정 상태(입점, 입점신청 등)와 변화될 상태 id를 가져오는 함수

        Args:
            conn (Connection): DB 커넥션 객체
            seller_status_type (dict) :                 
                "seller_status_type_button": [
                        {
                            "button_name": 상태 변경 버튼
                            "to_status_type_id": 상태 변경 후 변경될 seller_status_type_id
                        },
                        {
                            "button_name": 상태 변경 버튼
                            "to_status_type_id": 상태 변경 후 변경될 seller_status_type_id
                        }
                    ],

        """

        sql = """
            SELECT 
                sst.name AS status_name,
                sstb.seller_status_type_id,
                sstb.seller_status_button_id,
                ssb.name AS button_name,
                ssb.to_status_type_id
            FROM 
                seller_status_type AS sst
            INNER JOIN 
                seller_status_type_button AS sstb ON sstb.seller_status_type_id = sst.id
            LEFT OUTER JOIN
                seller_status_button AS ssb
                ON ssb.id = sstb.seller_status_button_id
            WHERE
                sst.name = %(seller_status_type)s
            ORDER BY sst.id ASC;
        """

        with conn.cursor() as cursor:
            cursor.execute(sql, {"seller_status_type":seller_status_type})
            return cursor.fetchall()
            

    def get_seller_list(self, conn, params, headers):
        """ 셀러 계정 리스트

        셀러 계정 관리에서 셀러 리스트를 가져오는 함수

        Args:
            conn (Connection): DB 커넥션 객체
            params (dict): 셀러 계정 리스트 표출을 위한 필터링 데이터
                {
                    "seller_id": 셀러 번호,
                    "seller_identification": 셀러아이디,
                    "english_brand_name": 영어 브랜드명,
                    "korean_brand_name": 한글 브랜드명,
                    "manager_name": 담당자 이름,
                    "seller_status_type" : 셀러 계정 상태,
                    "manager_email": 담당자 이메일,
                    "sub_property": 셀러 속성,
                    "seller_created_date": 셀러 계정 생성 날짜
                }

        """
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
                s.created_at as seller_created_date
        """

        condition = """
            FROM 
                sellers as s
            INNER JOIN
                managers as m ON m.id = (
                    SELECT MIN(id) FROM managers WHERE seller_id = s.id
                )
            INNER JOIN
                sub_property as sb ON s.sub_property_id = sb.id
            INNER JOIN
                seller_status_type as sst ON sst.id = s.seller_status_type_id
            WHERE
                    s.created_at BETWEEN '0000-00-00 00:00:00' AND '9999-12-30 00:00:00'
                AND 
                    s.is_deleted = 0 
        """
        # is_deleted가 1인 것은 표출 안되도록 추가

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
                    %(offset)s
        """

        count = """
                COUNT(*) as count 
        """

        sql_select_seller_info = select + seller_info + condition + limit
        sql_select_seller_count = select + count + condition + limit
        with conn.cursor() as cursor:
            cursor.execute(sql_select_seller_info, params)
            seller_info_list = cursor.fetchall()

            if 'application/vnd.ms-excel' in headers.values():
                return seller_info_list

            cursor.execute(sql_select_seller_count, params)
            seller_counts = cursor.fetchone()

            return seller_info_list, seller_counts
    
    def change_seller_status_type(self, conn, params):
        """ 셀러 상태 변경 

        셀러의 입점 상태를 변경하는 함수

        Args:
            conn (Connection): DB커넥션 객체,
            params (dict): 
                {
                    'to_status_type_id': 변경될 셀러 상태 번호, 
                    'account_id': 회원 pk 번호, 
                    'seller_id': 셀러 pk 번호
                }
        """
        sql = """
            UPDATE 
                sellers 
            SET
                seller_status_type_id = %(to_status_type_id)s
            WHERE   
                id = %(seller_id)s
        """

        with conn.cursor() as cursor:
            cursor.execute(sql, params)

    def check_if_store_out(self, conn, params):
        """ 현재 스토어 퇴점 확인

        현재 스토어가 퇴점했는지 아닌지 확인하는 함수

        Args:
            conn (Connection): DB커넥션 객체
            params (dict): 
                {
                    'to_status_type_id': 변경될 셀러 상태 번호, 
                    'account_id': 회원 pk 번호, 
                    'seller_id': 셀러 pk 번호
                }
        
        Returns:
            cursor.fetchone() (dict): 
                {
                    'seller_status_type_id': 현재 셀러 상태 아이디
                }
        """

        sql = """
            SELECT
                seller_status_type_id
            FROM
                sellers
            WHERE
                id = %(seller_id)s
        """
        
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()

    def change_seller_is_deleted(self, conn, params):
        """ 셀러 삭제

        셀러를 삭제하는 함수

        Args:
            conn (Connection): DB커넥션 객체
            params (dict): 
                {
                    'to_status_type_id': 변경될 셀러 상태 번호, 
                    'account_id': 회원 pk 번호, 
                    'seller_id': 셀러 pk 번호
                }
        """

        sql = """
            UPDATE 
                sellers
            SET 
                is_deleted = 1
            WHERE
                id = %(seller_id)s
        """

        with conn.cursor() as cursor:
            cursor.execute(sql, params)


    def change_seller_history(self, conn, params):
        """셀러 히스토리 변경

        셀러의 히스토리를 변경하는 함수

        Args:
            conn (Connection): DB커넥션 객체
            params (dict): 
                {
                    'to_status_type_id': 변경될 셀러 상태 번호, 
                    'account_id': 회원 pk 번호, 
                    'seller_id': 셀러 pk 번호
                }
        """

        sql = """
            INSERT INTO sellers_history(
                seller_id,
                modify_account_id,
                is_deleted,
                property_id,
                sub_property_id,
                seller_status_type_id,
                zip_code,
                address,
                detail_address,
                korean_brand_name,
                english_brand_name,
                customer_center_number,
                profile_image_url,
                background_image_url,
                description,
                detail_description,
                open_at,
                close_at
            )
            SELECT 
                id,
                %(account_id)s,
                is_deleted,
                property_id,
                sub_property_id,
                seller_status_type_id,
                zip_code,
                address,
                detail_address,
                korean_brand_name,
                english_brand_name,
                customer_center_number,
                profile_image_url,
                background_image_url,
                description,
                detail_description,
                open_at,
                close_at
            FROM
                sellers 
            WHERE id = %(seller_id)s
        """

        with conn.cursor() as cursor:
            cursor.execute(sql, params)
    
    def get_seller_info(self, conn, params):
        """ 셀러 상세 정보

        셀러 수정 페이지에서 셀러의 상세 정보를 가져오는 함수

        Args:
            conn (Connection): DB커넥션 객체
            params (dict): {"seller_identification" : 셀러 아이디}

        Returns:
            seller_info (dict) : 
                {
                    'seller_id': 셀러 id, 
                    'seller_identification': 셀러 아이디, 
                    'profile_image_url': 프로필 이미지 url,
                    'seller_status_type': 셀러 상태, 
                    'seller_status_type_id': 셀러 상태 id, 
                    'korean_brand_name': 한글 브랜드명, 
                    'english_brand_name': 영어 브랜드명, 
                    's.seller_identification': 셀러 아이디, 
                    'background_image_url': 배경이미지 url, 
                    'description': 셀러 설명, 
                    'detail_description': 셀러 상세 설명, 
                    'customer_center': 고객센터, 
                    'customer_center_number': 고객센터 번호, 
                    'zip_code': 우편번호, 
                    'address': 주소, 
                    'detail_address': 상세 주소, 
                    'open_at': 고객센터 시작 시간, 
                    'close_at': 고객센터 마감 시간, 
                    'delivery_info': 배송 정보, 
                    'exchange_refund_info': 교환, 환불 정보
                }
            manager_info (list):
                [
                    {
                        'seller_id': 셀러 id, 
                        'manager_name': 매니저 이름, 
                        'manager_phone': 매니저 전화번호, 
                        'manager_email': 매니저 이메일
                    }
                ]
        """

        sql_select_seller = """
            SELECT
                s.id AS seller_id,
                s.seller_identification,
                s.profile_image_url,
                sst.name AS seller_status_type,
                s.seller_status_type_id,
                s.korean_brand_name,
                s.english_brand_name,
                s.seller_identification,
                s.background_image_url,
                s.description,
                s.detail_description,
                s.customer_center,
                s.customer_center_number,
                s.zip_code,
                s.address,
                s.detail_address,
                s.open_at,
                s.close_at, 
                s.delivery_info,
                s.exchange_refund_info
            FROM
                sellers AS s
            INNER JOIN
                seller_status_type AS sst ON s.seller_status_type_id = sst.id
            WHERE
                s.id = %(seller_id)s
        """

        sql_select_manager = """
            SELECT
                s.id AS seller_id,
                m.id AS manager_id,
                m.name AS manager_name,
                m.phone AS manager_phone,
                m.email AS manager_email
            FROM 
                sellers AS s
            INNER JOIN
                managers AS m ON s.id = m.seller_id
            WHERE 
                    s.id = %(seller_id)s
                AND
                    m.is_deleted = 0;
        """
        
        with conn.cursor() as cursor:
            cursor.execute(sql_select_seller, params)
            seller_info = cursor.fetchone()
            
        
        with conn.cursor() as cursor:
            cursor.execute(sql_select_manager, params)
            manager_info = cursor.fetchall()

            return seller_info, manager_info


    def get_managers_info(self, conn, params):
        """ 현재 셀러의 담당자 정보

        현재 셀러의 담당자의 정보들을 가져오는 함수

        Args:
            conn (Connection): DB커넥션 객체
            params (dict): 
                {
                    'profile_image_url': 셀러 프로필 이미지, 
                    'background_image_url': 배경 이미지, 
                    'seller_sub_property': 셀러 2차 속성, 
                    'seller_sub_property_id': 2차 속성 id, 
                    'korean_brand_name': 셀러 한글 브랜드명, 
                    'english_brand_name': 셀러 영어 브랜드명, 
                    'description': 한 줄 소개, 
                    'detail_description': 상세 소개, 
                    'zip_code': 우편번호, 
                    'address': 주소, 
                    'detail_address': 상세주소, 
                    'customer_center': 고객센터, 
                    'customer_center_phone': 고객센터 전화번호, 
                    'customer_open_time': 고객센터 시작 시간, 
                    'customer_close_time': 고객센터 마감 시간, 
                    'delivery_info': 배송 정보, 
                    'exchange_refund_info': 교환/환불 정보, 
                    'account_id': 계정 id, 
                    'account_type_id': 계정 type id, 
                    'seller_id': 셀러 id
                }
        Returns: 
            cursor.fetchall() (list):
                [
                    {
                        'manager_id': 담당자 id, 
                        'seller_id': 셀러 id, 
                        "manager_name": 매니저,
                        "manager_email": 매니저 이메일,
                        "manager_phone": 매니저 전화번호
                    }, 
                    {
                        'manager_id': 담당자 id, 
                        'seller_id': 셀러 id, 
                        "manager_name": 매니저,
                        "manager_email": 매니저 이메일,
                        "manager_phone": 매니저 전화번호
                    }
                ]
        """

        sql = """
            SELECT
                id AS manager_id,
                seller_id,
                name AS manager_name,
                phone AS manager_phone,
                email AS manager_email
            FROM
                managers
            WHERE
                    seller_id = %(seller_id)s
                AND
                    is_deleted = 0
        """

        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
            

    def update_managers_info(self, conn, manager_params):
        """ 담당자 정보를 수정

        담당자 정보를 수정하고 history를 추가하는 함수

        Args:
            conn (Connection): DB커넥션 객체
            manager_params (list):
                [
                    {
                        "manager_name": 매니저,
                        "manager_email": 매니저 이메일,
                        "manager_phone": 매니저 전화번호
                        'account_id': 계정 id, 
                        'manager_id': 담당자 id, 
                        'seller_id': 셀러 id, 
                    }, 
                    {
                        "manager_name": 매니저,
                        "manager_email": 매니저 이메일,
                        "manager_phone": 매니저 전화번호
                        'account_id': 계정 id, 
                        'manager_id': 담당자 id, 
                        'seller_id': 셀러 id, 
                    }
                ]
        """

        sql = """
            UPDATE
                managers
            SET
                name = %(manager_name)s,
                email = %(manager_email)s,
                phone = %(manager_phone)s
            WHERE
                id = %(manager_id)s
            """

        with conn.cursor() as cursor:
            cursor.executemany(sql, manager_params)

    def delete_managers_info(self, conn, current_managers_in_db):
        """ 담당자 정보 삭제

        담당자 정보를 삭제하는 함수 (논리 삭제)

        Args:
            conn (Connection): DB커넥션 객체
            current_managers_in_db (list):
                [
                    {
                        "manager_name": 매니저,
                        "manager_email": 매니저 이메일,
                        "manager_phone": 매니저 전화번호
                        'account_id': 계정 id, 
                        'manager_id': 담당자 id, 
                        'seller_id': 셀러 id, 
                    }
                ]
        """

        sql = """
            UPDATE
                managers
            SET
                is_deleted = 1
            WHERE
                id = %(manager_id)s
        """
        
        with conn.cursor() as cursor:
            cursor.executemany(sql, current_managers_in_db)

    def insert_managers_info(self, conn, manager_params):
        """ 담당자 정보 추가 

        담당자 정보를 추가하는 함수

        Args:
            conn (Connection): DB커넥션 객체
            manager_params (list):
                [
                    {
                        "manager_name": 매니저,
                        "manager_email": 매니저 이메일,
                        "manager_phone": 매니저 전화번호
                        'account_id': 계정 id, 
                        'seller_id': 셀러 id, 
                    }
                ]
        """
        
        manager_list = list()
        for manager in manager_params:
            sql_insert = """
                INSERT INTO managers (
                    seller_id,
                    name,
                    phone,
                    email
                ) VALUES (
                    %(seller_id)s,
                    %(manager_name)s,
                    %(manager_phone)s,
                    %(manager_email)s
                )
            """

            sql_select = """
                SELECT
                    id AS manager_id,
                    seller_id,
                    name AS manager_name,
                    phone AS manager_phone,
                    email AS manager_email
                FROM
                    managers
                WHERE
                    id = (SELECT last_insert_id())
            """

            with conn.cursor() as cursor:
                cursor.execute(sql_insert, manager)
            
            with conn.cursor() as cursor:
                cursor.execute(sql_select)
                manager_list.append(cursor.fetchone())
        
        return manager_list

    def insert_managers_history(self, conn, manager_params):
        """ 담당자 history 추가

        담당자 정보가 수정됐을 때 history에 추가하는 함수

        Args:
            conn (Connection): DB커넥션 객체
            manager_params (list):
                [
                    {
                        "manager_name": 매니저,
                        "manager_email": 매니저 이메일,
                        "manager_phone": 매니저 전화번호
                        'account_id': 계정 id, 
                        'manager_id': 담당자 id, 
                        'seller_id': 셀러 id, 
                    }
                ]
        """

        sql = """
            INSERT INTO managers_history (
                manager_id,
                name,
                phone,
                email,
                is_deleted,
                modify_account_id
            ) 
            SELECT 
                id,
                name,
                phone,
                email,
                is_deleted,
                %(account_id)s
            FROM
                managers
            WHERE
                id= %(manager_id)s
                
        """

        with conn.cursor() as cursor:
            cursor.executemany(sql, manager_params)


    def update_seller_info(self, conn, params):
        """ 셀러 정보를 수정하는 함수

        셀러 정보를 수정하는 함수

        Args:
            conn (Connection): DB커넥션 객체
            params (dict): 
                {
                    'profile_image_url': 셀러 프로필 이미지, 
                    'background_image_url': 배경 이미지, 
                    'seller_sub_property': 셀러 2차 속성, 
                    'seller_sub_property_id': 2차 속성 id, 
                    'korean_brand_name': 셀러 한글 브랜드명, 
                    'english_brand_name': 셀러 영어 브랜드명, 
                    'description': 한 줄 소개, 
                    'detail_description': 상세 소개, 
                    'zip_code': 우편번호, 
                    'address': 주소, 
                    'detail_address': 상세주소, 
                    'customer_center': 고객센터, 
                    'customer_center_phone': 고객센터 전화번호, 
                    'customer_open_time': 고객센터 시작 시간, 
                    'customer_close_time': 고객센터 마감 시간, 
                    'delivery_info': 배송 정보, 
                    'exchange_refund_info': 교환/환불 정보, 
                    'account_id': 계정 id, 
                    'account_type_id': 계정 type id, 
                    'seller_id': 셀러 id
                }
        """

        sql = """
            UPDATE
                sellers
            SET
                property_id = (SELECT property_id FROM sub_property WHERE id = %(seller_sub_property_id)s),
                sub_property_id = %(seller_sub_property_id)s,
                zip_code = %(zip_code)s,
                address = %(address)s,
                detail_address = %(detail_address)s,
                korean_brand_name = %(korean_brand_name)s,
                english_brand_name = %(english_brand_name)s,
                customer_center_number = %(customer_center_phone)s,
                customer_center = %(customer_center)s,
                profile_image_url =%(profile_image_url)s,
                background_image_url =%(background_image_url)s,
                description = %(description)s,
                detail_description = %(detail_description)s,
                open_at = %(customer_open_time)s,
                close_at = %(customer_close_time)s
            WHERE
                id = %(seller_id)s;
            """

        with conn.cursor() as cursor:
            cursor.execute(sql, params)
    
    
    def insert_seller_history(self, conn, params):
        """ 셀러 history 수정

        셀러 history를 수정하는 함수

        Args:
            conn (Connection): DB커넥션 객체
            params (dict): 
                {
                    'profile_image_url': 셀러 프로필 이미지, 
                    'background_image_url': 배경 이미지, 
                    'seller_sub_property': 셀러 2차 속성, 
                    'seller_sub_property_id': 2차 속성 id, 
                    'korean_brand_name': 셀러 한글 브랜드명, 
                    'english_brand_name': 셀러 영어 브랜드명, 
                    'description': 한 줄 소개, 
                    'detail_description': 상세 소개, 
                    'zip_code': 우편번호, 
                    'address': 주소, 
                    'detail_address': 상세주소, 
                    'customer_center': 고객센터, 
                    'customer_center_phone': 고객센터 전화번호, 
                    'customer_open_time': 고객센터 시작 시간, 
                    'customer_close_time': 고객센터 마감 시간, 
                    'delivery_info': 배송 정보, 
                    'exchange_refund_info': 교환/환불 정보, 
                    'account_id': 계정 id, 
                    'account_type_id': 계정 type id, 
                    'seller_id': 셀러 id
                }  
        """
        
        sql = """
            INSERT INTO sellers_history (
                seller_id,
                modify_account_id,
                is_deleted,
                property_id,
                sub_property_id,
                seller_status_type_id,
                zip_code,
                address,
                detail_address,
                korean_brand_name,
                english_brand_name,
                customer_center_number,
                profile_image_url,
                background_image_url,
                description,
                detail_description,
                open_at,
                close_at
            )
            SELECT
                id,
                %(account_id)s,
                is_deleted,
                property_id,
                sub_property_id,
                seller_status_type_id,
                zip_code,
                address,
                detail_address,
                korean_brand_name,
                english_brand_name,
                customer_center_number,
                profile_image_url,
                background_image_url,
                description,
                detail_description,
                open_at,
                close_at
            FROM
                sellers
            WHERE
                id = %(seller_id)s;
        """

        with conn.cursor() as cursor:
            cursor.execute(sql, params)