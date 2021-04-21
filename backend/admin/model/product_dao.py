class ProductDao:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def get_products_list(self, conn, params):
        pass

    # 지금 작업하는 부분 ~~~~
    def post_product_by_seller_or_master(self, conn, body):
        pass

    def patch_product_selling_or_display_status(self, conn, body):
        pass
    
    def get_product_detail(self, conn, product_code):
        pass

    def search_seller(self, conn, keyword):
        # seller의 상호명에서 keyword 값으로 시작하는 값들을 찾기
        sql = """
            SELECT
                s.id,
                s.profile_image_url,
                s.korean_brand_name
            FROM
                sellers AS s
            WHERE
                korean_brand_name
                LIKE
                    %(keyword)s
            LIMIT 10
        """
        params = dict()
        params['keyword'] = keyword
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    def get_property_and_available_categories_list(self, conn, seller_id):
        sql = """
            SELECT
                p.id,
                p.name,
                c.id,
                c.name
            FROM
                sellers AS s
            INNER JOIN
                property as p ON s.property_id = p.id
            INNER JOIN
                category as c ON p.id = c.property_id
            WHERE
                s.id = %(seller_id)s
        """
        params ={}
        params['seller_id'] = seller_id
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    def get_sub_categories_list(self, conn, category_id):
        sql="""
            SELECT
                c.id,
                c.name
            FROM
                category AS c
            WHERE
                property_id = %(category_id)s
        """
        params = {}
        params['category_id'] = category_id
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def get_products_color_list(self, conn):
        sql = """
            SELECT 
                *
            FROM
                color
        """
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_products_size_list(self, conn):
        sql = """
            SELECT
                *
            FROM
                size
        """
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()