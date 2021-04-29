
class ProductDao:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def get_products_list(self, conn, params, headers):
        sql_select = """
            SELECT
                p.created_at as upload_date,
                pi.image_url,
                p.title,
                p.product_code,
                p.id,
                p.seller_id,
                p.price,
                p.discount_rate,
                p.price - (p.price * p.discount_rate) DIV 1 as discount_price,
                p.is_displayed,
                p.is_selling,
                s.korean_brand_name,
                sp.name as sub_property
        """
        sql_select1 = """
            SELECT
                count(0) as total_count
        """

        sql = """
            FROM
                products as p
            INNER JOIN 
                product_images as pi
                ON p.id = pi.product_id
                AND pi.is_represent = 1
            INNER JOIN 
                sellers as s
                ON p.seller_id = s.id
            INNER JOIN 
                sub_property as sp
                ON s.sub_property_id = sp.id
            WHERE
                1 + 1
        """
        
        sql1 = """
            ORDER BY
                p.created_at DESC
            LIMIT
                %(limit)s
            OFFSET
                %(page)s
        """
        # 판매, 미판매 여부 
        if 'selling' in params:
            sql += """
                AND
                    p.is_selling = %(selling)s
            """
        # 진열 미진열 여부
        if 'displayed' in params:
            sql += """
                AND
                    p.is_displayed = %(displayed)s
            """
        # 속성 리스트에 존재하는 셀러 선택
        if 'sub_property' in params:
            sql += """
                AND
                    s.sub_property_id IN %(sub_property)s
            """
        # 할인여부 중 할인
        if 'discount' in params and params['discount'] :
            sql += """
                AND
                    p.discount_rate > 0
            """
        # 할인여부 중 미할인
        if 'discount' in params and not params['discount'] :
            sql += """
                AND
                    p.discount_rate = 0
            """
        # 셀러명으로 검색
        if 'seller' in params:
            sql += """
                AND
                    s.korean_brand_name = %(seller)s
            """
        # 상품 코드로 검색
        if 'product_code' in params:
            sql += """
                AND
                    p.product_code = %(product_code)s
            """
        # 상품명으로 검색
        if 'product_name' in params:
            sql += """
                AND
                    p.title = %(product_name)s
            """
        # 상품 번호로 검색
        if 'product_number' in params:
            sql += """
                AND
                    p.id = %(product_number)s
            """
        # 조회 날짜 시작, 끝 모두 선택 됐을 때 검색
        if 'start_date' in params and 'end_date' in params:
            sql += """
                AND
                    p.created_at >= %(start_date_str)s AND p.created_at < %(end_date_str)s
            """
        # 조회 날짜 시작 선택 됐을 때 검색
        if 'start_date' in params and 'end_date' not in params:
            sql += """
                AND
                    p.created_at >= %(start_date_str)s
            """
        # # 조회 날짜 끝 선택 됐을 때 검색
        if 'start_date' not in params and 'end_date' in params:
            sql += """
                AND
                    p.created_at < %(end_date_str)s
            """
        if 'select_product_id' in params:
            sql += """
                AND
                    p.id IN %(select_product_id)s
            """

        product_sql = sql_select + sql + sql1
        total_sql = sql_select1 + sql

        with conn.cursor() as cursor:
            cursor.execute(product_sql, params)
            product_result = cursor.fetchall()

            if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in headers.values():
                return product_result

            cursor.execute(total_sql, params)
            total_count_result = cursor.fetchone() 

            return product_result, total_count_result

    def create_product_info_dao(self, conn, params: dict):
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
                simple_description,
                content,
                product_code,
                manufacturer,
                date_of_manufacture,
                origin,
                price,
                discount_rate,
                discount_start_date,
                discount_end_date,
                min_amount,
                max_amount
                )
            VALUES (
                %(seller_id)s,
                %(property_id)s,
                %(category_id)s,
                %(sub_category_id)s,
                %(is_selling)s,
                %(is_displayed)s,
                %(title)s,
                %(simple_description)s,
                %(content)s,
                %(product_code)s,
                %(manufacturer)s,
                %(date_of_manufacture)s,
                %(origin)s,
                %(price)s,
                %(discount_rate)s,
                %(discount_start_date)s,
                %(discount_end_date)s,
                %(min_amount)s,
                %(max_amount)s
            )
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.lastrowid
    
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
            return cursor.lastrowid

    def insert_image_url_dao(self, conn, params: list):
        sql="""
            INSERT INTO
            product_images (
                product_id,
                image_url,
                is_represent,
                is_deleted,
                created_account_id,
                delete_account_id,
                deleted_at
            )
            VALUES (
                %(product_id)s,
                %(image_url)s,
                %(is_represent)s,
                %(is_deleted)s,
                %(created_account_id)s,
                %(delete_account_id)s,
                %(deleted_at)s
            )
        """
        with conn.cursor() as cursor:
            cursor.executemany(sql, params)

    
    def patch_product_selling_or_display_status(self, conn, body):
        pass
    
    def get_product_detail(self, conn, product_code):
        pass

    def search_seller_dao(self, conn, params: dict):
        sql = """
            SELECT
                s.id AS seller_id,
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
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    def get_property_and_available_categories_list_dao(self, conn, params: dict):
        sql = """
            SELECT
                pr.id AS property_id,
                pr.name AS property_name,
                c.id AS category_id,
                c.name AS category_name
            FROM
                sellers AS s
            INNER JOIN
                property as pr ON s.property_id = pr.id
            INNER JOIN
                category as c ON pr.id = c.property_id
            WHERE
                s.id = %(seller_id)s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    def get_sub_categories_list_dao(self, conn, params: dict):
        sql = """
            SELECT
                s.id AS subcategory_id,
                s.name AS subcategory_name
            FROM
                sub_category AS s
            WHERE
                s.category_id = %(category_id)s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def get_products_color_list_dao(self, conn):
        sql = """
            SELECT 
                c.id AS color_id,
                c.name AS color_name
            FROM
                color AS c
        """
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_products_size_list_dao(self, conn):
        sql = """
            SELECT
                s.id AS size_id,
                s.name AS size_name
            FROM
                size AS s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
