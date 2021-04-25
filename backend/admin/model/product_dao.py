class ProductDao:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def get_products_list(self, conn, params):
        pass

    def create_basic_info_dao(self, conn, basic_info: dict):
        sql = """
            INSERT INTO
            products (
                seller_id,
                property_id,
                category_id,
                sub_category_id,
                is_selling,
                is_displayed,
                title,
                description,
                content,
                product_code
                )
            VALUES (
                %(seller_id)s,
                %(property_id)s,
                %(category_id)s,
                %(sub_category_id)s,
                %(title)s,
                %(description)s,
                %(content)s,
                %(product_code)s
            )
        """

        with conn.cursor() as cursor:
            cursor.execute(sql, basic_info)
            product_id = cursor.lastrowid
            return product_id
            
    
    def create_selling_info_dao(self, conn, selling_info: dict):
        sql = """
            INSERT INTO 
            products(
                price,
                discount_rate,
                discount_price,
                discount_start_date,
                discount_end_date,
                min_amount,
                max_amount
            )
            VALUES (
                %(price)s,
                %(discount_rate)s,
                %(discount_price)s,
                %(discount_start_date)s,
                %(discount_end_date)s,
                %(min_amount)s,
                %(max_amount)s
            )
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, selling_info)

    
    def create_option_info_dao(self, conn, option_info: list):
        sql = """
            INSERT INTO
            options (
                product_id,
                color_id,
                size_id,
                price,
                stock,
                option_code
            )
            VALUES (
                %(product_id)s,
                %(color_id)s,
                %(size_id)s,
                %(price)s,
                %(stock)s,
                %(option_code)s
            )
        """
        with conn.cursor() as cursor:
            cursor.executemany(sql, option_info)


    def create_image_url_dao(self, conn, product_id: int, images: list):
        sql = """
            INSERT INTO
            product_images (
                product_id,
                image_url,
                is_represent
            )
            VALUES (
                # product_id,
                %s,
                1 if idx = 0 else 0 # index 에 따라 대표 이미지 선택 
            )
        """

        with conn.cursor() as cursor:
            cursor.executemany(sql, images) # ? 
            return "SUCCESS"
    
    def patch_product_selling_or_display_status(self, conn, body):
        pass
    
    def get_product_detail(self, conn, product_code):
        pass

    def search_seller_dao(self, conn, keyword: str):
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
    
    def get_property_and_available_categories_list_dao(self, conn, seller_id: int):
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
        params = dict()
        params['seller_id'] = seller_id
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    def get_sub_categories_list_dao(self, conn, category_id: int):
        sql = """
            SELECT
                c.id,
                c.name
            FROM
                category AS c
            WHERE
                c.property_id = %(category_id)s
        """
        params = dict()
        params['category_id'] = category_id
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def get_products_color_list_dao(self, conn):
        sql = """
            SELECT 
                c.id,
                c.name
            FROM
                color AS c
        """
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_products_size_list_dao(self, conn):
        sql = """
            SELECT
                s.id,
                s.name
            FROM
                size AS s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()