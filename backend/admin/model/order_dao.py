import pymysql

class OrderDao:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass
    
    def get_order_list(self, conn, params):
        sql = """
            SELECT
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

        if "sub_property_id" in params:
            sql += """
                AND 
                    sp.id = %(sub_property_id)s
            """
        
        if "order_number" in params:
            sql += """
                AND 
                    o.order_number = %(order_number)s
            """
        
        if "order_detail_number" in params:
            sql += """
                AND
                    d.detail_order_number = %(order_detail_number)s
            """

        if "seller_name" in params:
            sql += """
                AND
                    s.korean_brand_name = %(seller_name)s
            """
        
        if "order_username" in params:
            sql += """
                AND 
                    o.order_username = %(order_username)s
            """
        
        if "phone" in params:
            sql += """
                AND
                    u.phone = %(phone)s
            """
        
        if "product_name" in params:
            sql += """
                AND
                    p.title = %(product_name)s
            """

        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def patch_order_status_type(self, conn, body):
        sql = """
            UPDATE 
                orders_detail
            SET
                order_status_type_id = %(order_status_id)s
            WHERE 
                orders_detail.id = %(order_detail_id)s  
        """

        with conn.cursor() as cursor:
            cursor.executemany(sql, body)
        
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