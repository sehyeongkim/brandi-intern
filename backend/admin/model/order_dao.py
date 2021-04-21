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

    # def get_order_detail(self, conn, params):
    #     pass

    def patch_order_status_type(self, conn, body):
        """
        body = 
            [
                {'order_detail_id': 1, 'order_status_id': 3}
                {'order_detail_id': 2, 'order_status_id': 3}
                {'order_detail_id': 3, 'order_status_id': 3}
            ]
        """

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
            # print(cursor._last_executed)
            # UPDATE 
            #     orders_detail
            # SET
            #     order_status_type_id = 2
            # WHERE 
            #     orders_detail.id = 3  
        
            


            
            