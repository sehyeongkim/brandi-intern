class ProductDao:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def get_products_list(self, conn, params):
        pass

    def post_product_by_seller_or_master(self, conn, body):
        pass

    def patch_product_selling_or_display_status(self, conn, body):
        pass

    def get_product_detail(self, conn, product_code):
        pass
    
    def get_categories_list(self, conn, category_id):
        pass

    def get_sellers_list(self, conn, seller_id):
        pass

    def search_seller(self, conn, params):
        pass

    def get_products_color_list(self, conn):
        with conn.cursor() as cursor:
            sql = """
                    SELECT 
                    *
                    FROM
                    color
                """
            cursor.execute(sql)
            result = cursor.fetchall()

            return result

    def get_products_size_list(self, conn):
        with conn.cursor() as cursor:
            sql = """
                    SELECT
                    *
                    FROM
                    size
                """
            cursor.execute(sql)
            result = cursor.fetchall()
            
            return result