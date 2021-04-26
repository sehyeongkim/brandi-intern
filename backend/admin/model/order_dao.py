import pymysql

class OrderDao:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass
    
    def get_order_list(self, conn, params):
        """ 주문 조회 리스트 dao

        주문 조회 리스트 정보를 DB에서 가져오기 위한 함수

        Args:
            conn (Connection): DB 커넥션 객체
            params (dict) : query parameter로 받은 정보 (셀러명, 조회 기간 등)
        
        Returns:
            dict : 주문 리스트 정보
            dict : 주문 전체 개수
        """

        select = """ 
            SELECT 
        """
        order_info = """
                DATE_FORMAT(o.created_at, '%%Y-%%m-%%d %%h:%%i:%%s') AS created_at,
                o.order_number, 
                d.detail_order_number, 
                s.korean_brand_name,
                p.title,  
                p.discount_rate,
                p.discount_start_date,
                p.discount_end_date,
                si.name AS size_name, 
                c.name AS color_name, 
                d.quantity,
                o.order_username,
                u.phone AS orderer_phone,
                d.price,
                ost.name AS order_status_type
        """

        condition = """    
            FROM 
                orders as o
            INNER JOIN 
                orders_detail as d ON o.id = d.order_id
            INNER JOIN 
                products as p ON p.id = d.product_id 
            INNER JOIN 
                sellers as s ON s.id = p.seller_id 
            INNER JOIN 
                options as op ON op.product_id = p.id
            INNER JOIN 
                users AS u ON u.id = o.user_id
            INNER JOIN 
                sub_property as sp ON sp.id = s.sub_property_id
            INNER JOIN
                color as c ON op.color_id = c.id
            INNER JOIN
                size as si ON si.id = op.size_id
            INNER JOIN 
                order_status_type as ost ON ost.id = d.order_status_type_id
            WHERE 
                    o.created_at BETWEEN %(start_date)s AND %(end_date)s
                AND 
                    d.order_status_type_id=%(order_status_type_id)s
        """ 
        
        sql_1 = select + order_info + condition

        if "sub_property_id" in params:
            sql_1 += """
                AND 
                    sp.id = %(sub_property_id)s
            """
        
        if "order_number" in params:
            sql_1 += """
                AND 
                    o.order_number = %(order_number)s
            """
        
        if "order_detail_number" in params:
            sql_1 += """
                AND
                    d.detail_order_number = %(order_detail_number)s
            """

        if "seller_name" in params:
            sql_1 += """
                AND
                    s.korean_brand_name = %(seller_name)s
            """
        
        if "order_username" in params:
            sql_1 += """
                AND 
                    o.order_username = %(order_username)s
            """
        
        if "phone" in params:
            sql_1 += """
                AND
                    u.phone = %(orderer_phone)s
            """
        
        if "product_name" in params:
            sql_1 += """
                AND
                    p.title = %(product_name)s
            """
        
        sql_1 += """
                LIMIT
                    %(limit)s
                OFFSET
                    %(page)s
        """

        count = """
                COUNT(*) as count 
        """
        
        sql_2 = select + count + condition

        if "sub_property_id" in params:
            sql_2 += """
                AND 
                    sp.id = %(sub_property_id)s
            """
        
        if "order_number" in params:
            sql_2 += """
                AND 
                    o.order_number = %(order_number)s
            """
        
        if "order_detail_number" in params:
            sql_2 += """
                AND
                    d.detail_order_number = %(order_detail_number)s
            """

        if "seller_name" in params:
            sql_2 += """
                AND
                    s.korean_brand_name = %(seller_name)s
            """
        
        if "order_username" in params:
            sql_2 += """
                AND 
                    o.order_username = %(order_username)s
            """
        
        if "phone" in params:
            sql_2 += """
                AND
                    u.phone = %(orderer_phone)s
            """
        
        if "product_name" in params:
            sql_2 += """
                AND
                    p.title = %(product_name)s
            """

        with conn.cursor() as cursor:
            cursor.execute(sql_1, params)
            result_1 = cursor.fetchall()

            cursor.execute(sql_2, params)
            result_2 = cursor.fetchone()
            
            return result_1, result_2
        

    def check_if_status_type_exists(self, conn, body):
        exist_list = list()
        non_exist_list = list()
        for data in body:
            sql = """
                SELECT
                   1
                FROM
                    order_status_type
                WHERE 
                    id = %(order_status_type_id)s
            """
            with conn.cursor() as cursor:
                cursor.execute(sql, data)
                if cursor.fetchone():
                    exist_list.append(data)
                else:
                    non_exist_list.append(data)
                
        return exist_list, non_exist_list


    def check_if_possible_change(self, conn, body):
        PURCHASE_COMPLETE = 4
        CANCEL_COMPLETE = 7
        REFUND_COMPLETE = 9

        possible_list = list()
        impossible_list = list()
        for data in body:
            sql = """
                SELECT
                    id AS order_detail_id,
                    order_status_type_id
                FROM
                    orders_detail
                WHERE
                    id = %(orders_detail_id)s
            """

            with conn.cursor() as cursor:
                cursor.execute(sql, data)
                if cursor.fetchone()["order_status_type_id"] in (PURCHASE_COMPLETE, CANCEL_COMPLETE, REFUND_COMPLETE):
                    impossible_list.append(data)
                else:
                    possible_list.append(data)
        
        return possible_list, impossible_list


    def patch_order_status_type(self, conn, possible_to_patch):
        """ DB에서 주문 및 배송처리 함수

        DB에서 해당하는 row의 주문 상태를 변경해줌

        Args: 
            conn (Connection): DB 커넥션 객체
            possible_change_order_status (list): order_service에서 걸러진 주문들 (주문 상태를 변경하지 못하는 주문들은 제외됨)
        """

        sql = """
            UPDATE 
                orders_detail
            SET
                order_status_type_id = %(order_status_type_id)s
            WHERE 
                orders_detail.id = %(orders_detail_id)s  
        """

        with conn.cursor() as cursor:
            cursor.executemany(sql, possible_to_patch)

        
    def insert_order_detail_history(self, conn, results):
        """주문 히스토리 데이터 삽입

        주문 상태 변경 후 주문 히스토리에 row를 추가함

        Args:
            conn (Connection) : DB 커넥션 객체
            results (list) : 
                [
                    {"orders_detail_id" : 주문 상세 아이디, "order_status_type_id": 변경할 주문 상태 아이디},
                    {"orders_detail_id" : 주문 상세 아이디, "order_status_type_id": 변경할 주문 상태 아이디},
                    {"orders_detail_id" : 주문 상세 아이디, "order_status_type_id": 변경할 주문 상태 아이디}
                    ...
                ]
        """
        # account_id는 로그인 데코레이터로 파악
        for data in results:
            sql_1 = """
                SELECT 
                    id,
                    order_status_type_id,
                    address_id,
                    price
                FROM
                    orders_detail
                WHERE 
                    id = %(orders_detail_id)s
            """

            with conn.cursor() as cursor:
                cursor.execute(sql_1, data)
                result = cursor.fetchone()
                
            sql_2 = """
                INSERT INTO order_detail_history ( 
                    order_detail_id,
                    order_status_type_id,
                    address_id,
                    modify_account_id,
                    price
                )
                VALUES (
                    %(id)s,
                    %(order_status_type_id)s,
                    %(address_id)s,
                    
                    %(price)s
                )
            """

            with conn.cursor() as cursor:
                cursor.execute(sql_2, result)

            
    def get_order(self, conn, params):
        """ 주문 상세 확인 

        주문 상세 정보를 가져옴

        Args:
            conn (Connection) : DB 커넥션 객체
            params (dict) : 
                {"detail_order_number" : 주문 상세 번호}
        
        Returns:
            dict : 주문과 관련된 상세 정보 반환 
            list : 주문 이력 반환
        """
        sql_1 = """
            SELECT 
                o.order_number, 
                DATE_FORMAT(o.created_at, '%%Y-%%m-%%d %%h:%%i:%%s') AS created_at,
                od.detail_order_number, 
                ost.name AS order_status_type, 
                u.phone as order_phone,
                p.id as product_id, 
                op.id as option_id, 
                p.price, 
                p.discount_rate, 
                p.discount_start_date, 
                p.discount_end_date, 
                p.title, 
                s.korean_brand_name, 
                c.name AS color, 
                si.name AS size, 
                od.quantity,  
                u.id as user_id, 
                ad.recipient, 
                ad.zip_code, 
                o.order_username as orderer_name,
                ad.address, 
                ad.detail_address, 
                ad.phone as recipient_phone,
                u.phone as orderer_phone, 
                dm.name as delivery_memo, 
                o.delivery_memo_request as delivery_memo_custom
            FROM 
                orders_detail as od
            INNER JOIN 
                orders as o ON o.id = od.order_id
            INNER JOIN
                products as p ON p.id = od.product_id
            INNER JOIN
                options as op ON op.id = p.id
            INNER JOIN
                users as u ON u.id = o.user_id
            INNER JOIN
                sellers as s ON s.id = p.seller_id
            INNER JOIN
                address as ad ON ad.id = od.address_id
            INNER JOIN
                delivery_memo as dm ON dm.id = o.delivery_memo_id
            INNER JOIN
                color as c ON op.color_id = c.id
            INNER JOIN
                size as si ON si.id = op.size_id
            INNER JOIN 
                order_status_type as ost ON ost.id = od.order_status_type_id
            WHERE  
                od.detail_order_number = %(detail_order_number)s;
        """

        sql_2 = """
            SELECT 
                DATE_FORMAT(odh.updated_at, '%%Y-%%m-%%d %%h:%%i:%%s') AS updated_at,
                ost.name AS order_status_type
            FROM 
                orders_detail AS od
            INNER JOIN
                order_detail_history AS odh ON od.id = odh.order_detail_id
            INNER JOIN
                order_status_type AS ost ON ost.id = odh.order_status_type_id
            WHERE 
                od.detail_order_number = %(detail_order_number)s;
        """

        with conn.cursor() as cursor:
            cursor.execute(sql_1, params)
            result_1 = cursor.fetchone()

            cursor.execute(sql_2, params)
            result_2 = cursor.fetchall()

            return result_1, result_2