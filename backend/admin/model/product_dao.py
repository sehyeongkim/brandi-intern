from flask import g
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

    def post_product_by_seller_or_master(self, conn, body):
        pass

    def patch_product_selling_or_display_status(self, conn, body):
        pass

    def get_product_detail(self, conn, params):
        sql = """
            SELECT
                p.product_code,
                p.is_selling,
                p.is_displayed,
                pp.name as property,
                c.name as category,
                sc.name as sub_category,
                p.manufacturer,
                p.date_of_manufacture,
                p.origin,
                p.title,
                IF(p.simple_description,p.simple_description,'') as simple_description,
                p.content,
                p.price,
                p.discount_rate,
                DATE_FORMAT(p.discount_start_date,'%%Y-%%m-%%d %%h:%%m:%%s') as discount_start_date,
                DATE_FORMAT(p.discount_end_date,'%%Y-%%m-%%d %%h:%%m:%%s') as discount_end_date,
                p.min_amount,
                p.max_amount
            FROM 
                products as p
            INNER JOIN
                sellers as s
                ON  p.seller_id = s.id
            INNER JOIN
                property as pp
                ON  s.property_id = pp.id
            INNER JOIN
                category as c
                ON  p.category_id = c.id
            INNER JOIN
                sub_category as sc
                ON  p.sub_category_id = sc.id
            WHERE
                p.product_code = %(product_code)s
            """

        params['account_id'] = g.account_id
        if g.account_type_id == 2:
            sql += """
                AND
                    s.account_id = %(account_id)s
            """

        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
    
    def get_product_images_by_product_code(self, conn, params):
        sql = """
            SELECT
                pi.image_url,
                pi.is_represent
            FROM
                product_images as pi
            INNER JOIN
                products as p
                ON p.id = pi.product_id
                AND p.product_code = %(product_code)s
            WHERE
                pi.is_deleted = 0
        """
        
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def get_product_options_by_product_code(self, conn, params):
        sql = """
            SELECT
                o.id,
                o.stock,
                c.name as color,
                s.name as size
            FROM
                options as o
            INNER JOIN
                products as p
                ON p.id = o.product_id
                AND p.product_code = %(product_code)s
            INNER JOIN
                color as c
                ON o.color_id = c.id
            INNER JOIN
                size as s
                ON o.size_id = s.id
            WHERE
                o.is_deleted = 0
        """

        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

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
