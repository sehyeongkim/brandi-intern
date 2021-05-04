import pymysql
from flask import g

from flask import g

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
            order_list_info (dict) : 주문 리스트 정보
            orders_count (dict) : 주문 전체 개수
        """

        select = """ 
            SELECT 
        """
        order_info = """
                o.created_at AS created_at,
                o.order_number, 
                d.id AS orders_detail_id,
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
        
        sql_select_info = select + order_info + condition

        if "sub_property_id" in params:
            sql_select_info += """
                AND 
                    sp.id = %(sub_property_id)s
            """
        
        if "order_number" in params:
            sql_select_info += """
                AND 
                    o.order_number = %(order_number)s
            """
        
        if "order_detail_number" in params:
            sql_select_info += """
                AND
                    d.detail_order_number = %(order_detail_number)s
            """

        if "seller_name" in params:
            sql_select_info += """
                AND
                    s.korean_brand_name = %(seller_name)s
            """
        
        if "order_username" in params:
            sql_select_info += """
                AND 
                    o.order_username = %(order_username)s
            """
        
        if "phone" in params:
            sql_select_info += """
                AND
                    u.phone = %(orderer_phone)s
            """
        
        if "product_name" in params:
            sql_select_info += """
                AND
                    p.title = %(product_name)s
            """
        
        sql_select_info += """
                LIMIT
                    %(limit)s
                OFFSET
                    %(page)s
        """

        count = """
                COUNT(*) as count 
        """
        
        sql_select_count = select + count + condition

        if "sub_property_id" in params:
            sql_select_count += """
                AND 
                    sp.id = %(sub_property_id)s
            """
        
        if "order_number" in params:
            sql_select_count += """
                AND 
                    o.order_number = %(order_number)s
            """
        
        if "order_detail_number" in params:
            sql_select_count += """
                AND
                    d.detail_order_number = %(order_detail_number)s
            """

        if "seller_name" in params:
            sql_select_count += """
                AND
                    s.korean_brand_name = %(seller_name)s
            """
        
        if "order_username" in params:
            sql_select_count += """
                AND 
                    o.order_username = %(order_username)s
            """
        
        if "phone" in params:
            sql_select_count += """
                AND
                    u.phone = %(orderer_phone)s
            """
        
        if "product_name" in params:
            sql_select_count += """
                AND
                    p.title = %(product_name)s
            """

        with conn.cursor() as cursor:
            cursor.execute(sql_select_info, params)
            order_list_info = cursor.fetchall()

            cursor.execute(sql_select_count, params)
            order_counts = cursor.fetchone()
            
            return order_list_info, order_counts
        
    def get_status_type(self, conn):
        """ 주문 상태 데이터

        DB에서 주문 상태 데이터를 가지고 오는 함수

        Args:
            conn (Connection): DB커넥션 객체
        
        Returns:
            [
                {
                    'id': 1, 
                    'name': '상품준비'
                }, 
                {
                    'id': 2, 
                    'name': '배송중'
                }, 
                {
                    'id': 3, 
                    'name': '배송완료'
                }, 
                {
                    'id': 4, 
                    'name': '구매확정'
                }, 
                {
                    'id': 5, 
                    'name': '반품요청'
                }, 
                {
                    'id': 6, 
                    'name': '취소요청'
                }, 
                {
                    'id': 7, 
                    'name': '취소완료'
                }, 
                {
                    'id': 8, 
                    'name': '환불요청'
                }, 
                {
                    'id': 9, 
                    'name': '환불완료'
                }, 
                {
                    'id': 10, 
                    'name': '결제대기'
                }, 
                {
                    'id': 11, 
                    'name': '결제완료'
                }
            ]
        """
        sql = """
            SELECT
                id,
                name
            FROM
                order_status_type

        """
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def check_if_possible_change(self, conn, body):
        """ 주문 상태를 변경할 수 있는지 확인

        구매확정, 환불완료 등 이미 변경할 수 없는 상태인지 확인하기 위한 함수

        Args:   
            conn (Connection): DB커넥션 객체
            body (list): 
                [
                    {
                        'orders_detail_id': 주문 상세 id, 
                        'order_status_type_id': 주문 상태 id
                    }
                ]
        
        Returns:
            order_detail_results (list):
                [
                    {
                        'orders_detail_id': 주문 상세 id, 
                        'order_status_type_id': 주문 상태 id
                    }
                ]
        """
        
        order_detail_results = list()
        for data in body:
            sql = """
                SELECT
                    id AS orders_detail_id,
                    order_status_type_id
                FROM
                    orders_detail
                WHERE
                    id = %(orders_detail_id)s
            """

            with conn.cursor() as cursor:
                cursor.execute(sql, data)
                order_detail_results.append(cursor.fetchone())
        return order_detail_results


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

        for data in results:
            sql = """
                INSERT INTO order_detail_history(
                    order_detail_id,
                    order_status_type_id,
                    address_id,
                    modify_account_id,
                    price
                )
                SELECT
                    id,
                    order_status_type_id,
                    address_id,
                    %(account_id)s,
                    price
                FROM
                    orders_detail
                WHERE
                    id = %(orders_detail_id)s
            """

            # modify account id를 위해서 추가
            data["account_id"] = g.account_id
            with conn.cursor() as cursor:
                cursor.execute(sql, data)

            
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
        sql_select_info = """
            SELECT 
                o.order_number, 
                o.created_at AS created_at,
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

        sql_select_history = """
            SELECT 
                odh.updated_at AS updated_at,
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
            cursor.execute(sql_select_info, params)
            order_info = cursor.fetchone()

            cursor.execute(sql_select_history, params)
            order_history = cursor.fetchall()

            return order_info, order_history

    def get_dashboard_seller(self, conn, account_id):
        #전체상품, 노출상품
        sql1 = """
                SELECT
                    COUNT(*) AS product_all,
                    COUNT(case when is_selling=1 then 1 end) AS product_selling
                FROM
                    account AS ac
                INNER JOIN sellers AS se
                    ON ac.id = se.account_id
                INNER JOIN products AS pr
                    ON se.id = pr.seller_id
                WHERE pr.seller_id = %(account_id)s;
                """
        # 상품준비, 배송완료
        sql2 =  """
                SELECT 
                    COUNT(case when od.order_status_type_id=1 then 1 end) AS before_delivery,
                    COUNT(case when od.order_status_type_id=3 then 1 end) AS complete_delivery
                FROM account AS ac
                INNER JOIN sellers AS se
                    ON ac.id = se.account_id
                INNER JOIN products AS pr
                    ON se.id = pr.seller_id
                INNER JOIN orders_detail AS od
                    ON pr.id = od.product_id
                WHERE pr.seller_id = %(account_id)s;
                """
        #30일간 결제건수, 결제금액
        sql3 = """
                SELECT 
                    COUNT(*) AS order_month,
                    SUM(od.price * od.quantity) AS sales_month
                FROM account AS ac
                INNER JOIN sellers AS se
                    ON ac.id = se.account_id
                INNER JOIN products AS pr
                    ON se.id = pr.seller_id
                INNER JOIN orders_detail AS od
                    ON pr.id = od.product_id
                WHERE pr.seller_id = %(account_id)s AND  od.order_status_type_id=4 AND od.updated_at BETWEEN DATE_ADD(NOW(),INTERVAL -1 MONTH ) AND NOW()
                """
                    
        params = dict()
        params['account_id'] = account_id

        with conn.cursor() as cursor:
            cursor.execute(sql1, params)
            result1 = cursor.fetchone()

            cursor.execute(sql2 , params)
            result2 = cursor.fetchone()

            cursor.execute(sql3, params)
            result3 = cursor.fetchone()
           
            result = {**result1, **result2, **result3}
        
            return result

       
