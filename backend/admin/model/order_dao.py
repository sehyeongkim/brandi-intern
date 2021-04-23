import pymysql

class OrderDao:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass
    
    def get_order_list(self, conn, params):
        select = """ 
            SELECT 
        """
        order_info = """
                o.created_at, 
                o.order_number, 
                d.detail_order_number, 
                s.korean_brand_name,
                p.title,  
                op.color_id, 
                op.size_id, 
                d.quantity,
                o.order_username,
                u.phone,
                d.price,
                d.order_status_type_id
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
            WHERE 
                    o.created_at BETWEEN %(date_from)s AND %(date_to)s
                AND 
                    d.order_status_type_id=%(order_status_id)s
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
                    u.phone = %(phone)s
            """
        
        if "product_name" in params:
            sql_1 += """
                AND
                    p.title = %(product_name)s
            """

        count = """
                COUNT(*) as count 
        """
        
        sql_2 = select + count + condition
        
        with conn.cursor() as cursor:
            sql = """
            SELECT o.created_at, o.order_number, d.detail_order_number, 
            s.korean_brand_name, p.title, op.color_id, op.size_id, d.quantity,
            u.email, u.phone, d.price, d.order_status_type_id
            FROM 
                orders as o
            JOIN 
                orders_detail as d ON o.id = d.order_id
            JOIN 
                products as p ON p.id = d.product_id 
            JOIN 
                sellers as s ON s.id = p.seller_id 
            JOIN 
                options as op ON op.product_id = p.id
            JOIN 
                users AS u ON u.id = o.user_id
            WHERE 
                o.created_at BETWEEN %(date_from)s AND %(date_to)s
            AND 
                d.order_status_type_id=%(order_status_id)s
            """ 
            results = cursor.execute(sql, {
                'date_from': params["date_from"],
                'date_to' : params["date_to"],
                'order_status_id': params["order_status_id"],
                # 'sub_property' : params['sub_property'],
                # 'order_no' : params['order_no'],
                # 'order_detail_no' : params['order_detail_no'],
                # 'user_name' : params['user_name'],
                # 'phone' : params['phone'],
                # 'seller_name' : params['seller_name'],
                # 'product_name' : params['product_name']
            })
            results = cursor.fetchall()
            return results

    def patch_order_status_type(self, conn, body):
        pass

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
                    COUNT(case when oh.order_status_type_id=11 then 1 end) AS order_month,
                    SUM(od.price*od.quantity) AS price_month
                FROM account AS ac
                INNER JOIN sellers AS se
                    ON ac.id = se.account_id
                INNER JOIN products AS pr
                    ON se.id = pr.seller_id
                INNER JOIN orders_detail AS od
                    ON pr.id = od.product_id
                INNER JOIN order_detail_history AS oh
                		ON oh.order_detail_id = od.id
                WHERE pr.seller_id = %(account_id)s AND oh.updated_at BETWEEN DATE_ADD(NOW(),INTERVAL -1 MONTH ) AND NOW();
                """
            
        params = dict()
        params['account_id'] = account_id

        with conn.cursor() as cursor:
            cursor.execute(sql1, params)
            result1 = cursor.fetchall()
            print(result1,'===============================')

            cursor.execute(sql2 , params)
            result2 = cursor.fetchall()
            print(result2,'===============================')

            cursor.execute(sql3, params)
            result3 = cursor.fetchall()
            print(result3,'===============================')

            return result1, result2, result3

    def patch_order_status_type(self, conn, possible_change_order_status):
        sql = """
            UPDATE 
                orders_detail
            SET
                order_status_type_id = %(order_status_type_id)s
            WHERE 
                orders_detail.id = %(order_detail_id)s  
        """

        with conn.cursor() as cursor:
            cursor.executemany(sql, possible_change_order_status)
    
    # DB에 값이 있는지 확인하기
    def check_appropriate_order_status_type(self, conn, body):
        sql = """
            SELECT 
                1
            FROM 
                order_status_type
            WHERE 
                id = %(order_status_id)s
        """

        with conn.cursor() as cursor:
            cursor.executemany(sql, body)
            results = cursor.fetchall()

            return results
    
    # 구매확정, 주문취소인 경우 바꿀 수 없음
    def check_current_order_status(self, conn, body):

        checked_current_order_status_list = list()
        for data in body:
            sql = """
                SELECT
                    id as order_detail_id,
                    order_status_type_id
                FROM 
                    orders_detail
                WHERE 
                    id = %(order_detail_id)s
            """

            with conn.cursor() as cursor:
                cursor.execute(sql, data)
                result = cursor.fetchone()
                checked_current_order_status_list.append(result)
        return checked_current_order_status_list
        
        
            
    
    def get_order(self, conn, params):
        sql_1 = """
            SELECT 
                o.order_number, 
                o.created_at, 
                od.detail_order_number, 
                od.order_status_type_id, 
                u.phone as order_phone,
                p.id as product_id, 
                op.id as option_id, 
                p.price, 
                p.discount_rate, 
                p.discount_start_date, 
                p.discount_end_date, 
                p.title, 
                s.korean_brand_name, 
                op.color_id, 
                op.size_id, 
                od.quantity,  
                u.id as user_id, 
                ad.recipient, 
                ad.zip_code, 
                ad.address, 
                ad.detail_address, 
                ad.phone as recipient_phone,
                u.phone as recipient_phone, 
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
            WHERE  
                od.detail_order_number = %(detail_order_number)s;
        """

        sql_2 = """
            SELECT 
                odh.updated_at,
                odh.order_status_type_id
            FROM 
                orders_detail as od
            INNER JOIN
                order_detail_history as odh ON od.id = odh.order_detail_id
            WHERE 
                od.detail_order_number = %(detail_order_number)s;
        """

        with conn.cursor() as cursor:
            cursor.execute(sql_1, params)
            result_1 = cursor.fetchone()

            cursor.execute(sql_2, params)
            result_2 = cursor.fetchall()

            return result_1, result_2
