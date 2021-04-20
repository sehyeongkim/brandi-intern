import pymysql

class OrderDao:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass
    
    def get_order_list(self, conn, params):
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

    # def get_order_detail(self, conn, params):
    #     pass

    def patch_order_status_type(self, conn, body):
        pass