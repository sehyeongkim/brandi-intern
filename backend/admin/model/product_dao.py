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
                DATE_FORMAT(p.created_at, '%%Y-%%m-%%d %%h:%%i:%%s') as upload_date,
                pi.image_url,
                p.title,
                p.product_code,
                p.id,
                p.seller_id,
                p.price,
                IF(p.discount_start_date <= NOW() AND p.discount_end_date <= NOW(), 0, round(p.discount_rate, 2)) as discount_rate,
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
        # 조회 날짜 끝 선택 됐을 때 검색
        if 'start_date' not in params and 'end_date' in params:
            sql += """
                AND
                    p.created_at < %(end_date_str)s
            """
        # 선택된 상품이 있을 때 해당 상품만 검색
        if 'select_product_id' in params:
            sql += """
                AND
                    p.id IN %(select_product_id)s
            """
        # 셀러계정일 때 해당 셀러상품만 검색
        if params['account_type_id'] == 2:
            sql += """
                AND
                    s.account_id = %(account_id)s
            """

        product_sql = sql_select + sql + sql1
        total_sql = sql_select1 + sql

        with conn.cursor() as cursor:
            cursor.execute(product_sql, params)
            product_result = cursor.fetchall()

            if 'application/vnd.ms-excel' in headers.values():
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
    
    def create_product_history(self, conn, params: dict):
        sql = """
            INSERT INTO
            product_history (
                product_id,
                modify_account_id,
                is_selling,
                is_displayed,
                title,
                simple_description,
                content,
                discount_rate,
                discount_start_date,
                discount_end_date,
                min_amount,
                max_amount
            )
            VALUES (
                %(product_id)s,
                %(modify_account_id)s,
                %(is_selling)s,
                %(is_displayed)s,
                %(title)s,
                %(simple_description)s,
                %(content)s,
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
            option_ids = list()
            for option in option_info:
                cursor.execute(sql, option)
                option_ids.append(cursor.lastrowid)
            return option_ids
    
    def create_option_history(self, conn, option_info: list):
        sql = """
            INSERT INTO
            options_history (
                option_id,
                price,
                modify_account_id,
                is_deleted
            )
            VALUES (
                %(option_id)s,
                %(price)s,
                %(modify_account_id)s,
                %(is_deleted)s
            )
        """
        with conn.cursor() as cursor:
            cursor.executemany(sql, option_info)

    def insert_image_url_dao(self, conn, params: list):
        sql="""
            INSERT INTO product_images (
                product_id,
                image_url,
                is_represent,
                created_account_id
            )
            VALUES (
                %(product_id)s,
                %(image_url)s,
                %(is_represent)s,
                %(created_account_id)s
            )
        """
        with conn.cursor() as cursor:
            cursor.executemany(sql, params)

    def patch_product_selling_or_display_status(self, conn, product_check_success_result):
        """상품 판매, 진열 상태 변경 함수

        요청 받은 상품 중 존재하거나 권한이 있는 상품의 판매, 진열여부를 변경한다.

        Arg:
            conn (Connection): DB 커넥션 객체
            product_check_success_result (list): service layer에서 걸러진 상품 리스트 
            
        """
        sql = """
            UPDATE
                products as p       
            SET
        """
        comma = ''
        
        if 'display' in product_check_success_result[0]:
            sql += """
                p.is_displayed = %(display)s
            """
            comma = ','
        
        if 'selling' in product_check_success_result[0]:
            sql += f"""
                {comma}p.is_selling = %(selling)s
            """
        sql1 = """
            WHERE
                p.id = %(product_id)s
        """
        sql += sql1
        with conn.cursor() as cursor:
            cursor.executemany(sql, product_check_success_result)


    def check_product_exists(self, conn, params):
        """데이터베이스 상품 존재여부 확인

        요청으로 들어온 상품 중 데이터베이스에 존재하면서 권한이 있는 상품 확인

        Arg:
            conn (Connection): DB 커넥션 객체
            params (list):
                [
                    {"product_id" : 상품아이디, "selling" : 판매여부, "display" : 진열여부},
                    {"product_id" : 상품아이디, "selling" : 판매여부, "display" : 진열여부},
                    {"product_id" : 상품아이디, "selling" : 판매여부, "display" : 진열여부}
                    ...
                ] 
        
        Return:
            [list]:
                [
                    {'product_id' : 상품아이디, 'is_exists' : 존재여부 0(비존재), 1(존재)},
                    {'product_id' : 상품아이디, 'is_exists' : 존재여부 0(비존재), 1(존재)},
                    {'product_id' : 상품아이디, 'is_exists' : 존재여부 0(비존재), 1(존재)}
                    ...
                ]
        """
        
        sql = """
            SELECT
                p.id as product_id
            FROM
                products as p
            INNER JOIN
                sellers as s
                ON s.id = p.seller_id
            WHERE
                p.id IN %(product_ids)s
        """

        if g.account_type_id == 2:
            sql  += """
                AND
                    s.account_id = %(account_id)s
            """

        product_ids = tuple(map(lambda d:d.get('product_id'), params))

        product_data = {
            'product_ids' : product_ids,
            'account_id' : g.account_id
        }

        with conn.cursor() as cousor:
            cousor.execute(sql, product_data)
            return cousor.fetchall()

    def insert_product_history(self, conn, params):
        """상품 히스토리 입력 함수

        변경된 상품의 이력을 남기는 함수

        Arg:
            conn (Connection): DB 커넥션 객체
            params (list):
                [
                    {"product_id" : 상품아이디, "selling" : 판매여부, "display" : 진열여부, 'is_exists' : 존재여부},
                    {"product_id" : 상품아이디, "selling" : 판매여부, "display" : 진열여부, 'is_exists' : 존재여부},
                    {"product_id" : 상품아이디, "selling" : 판매여부, "display" : 진열여부, 'is_exists' : 존재여부}
                    ...
                ] 

        """
        product_ids = tuple(map(lambda d:d.get('product_id'), params))
        sql = """
            INSERT INTO product_history(
                product_id,
                modify_account_id,
                is_selling,
                is_displayed,
                title,
                price,
                content,
                discount_rate,
                discount_start_date,
                discount_end_date,
                min_amount,
                max_amount
            )
            SELECT
                p.id,
                %(account_id)s,
                is_selling,
                is_displayed,
                title,
                price,
                content,
                discount_rate,
                discount_start_date,
                discount_end_date,
                min_amount,
                max_amount
            FROM
                products as p
            WHERE
                p.id IN %(product_ids)s
        """
        product_data = {
            'product_ids' : product_ids,
            'account_id' : g.account_id
        }
        with conn.cursor() as cursor:
            cursor.execute(sql, product_data)


    def get_product_detail(self, conn, params):
        sql = """
            SELECT
                p.product_code,
                p.is_selling,
                p.is_displayed,
                pp.name as property,
                pp.id as property_id,
                c.name as category,
                c.id as category_id,
                sc.name as sub_category,
                sc.id as sub_category_id,
                p.manufacturer,
                p.date_of_manufacture,
                p.origin,
                p.title,
                IF(p.simple_description,p.simple_description,'') as simple_description,
                p.content,
                p.price,
                p.discount_rate,
                p.discount_start_date as discount_start_date,
                p.discount_end_date as discount_end_date,
                p.min_amount,
                p.max_amount,
                p.id as product_id,
                s.korean_brand_name as seller_name
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
                c.id as color_id,
                s.name as size,
                s.id as size_id
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
    
    def patch_products_info(self, conn, params: dict):
        sql="""
            UPDATE products
            SET 
                seller_id = %(seller_id)s,
                property_id = %(property_id)s,
                category_id = %(category_id)s,
                sub_category_id = %(sub_category_id)s,
                is_selling = %(is_selling)s,
                is_displayed = %(is_displayed)s,
                title = %(title)s,
                simple_description = %(simple_description)s,
                content = %(content)s,
                price = %(price)s,
                discount_rate = %(discount_rate)s,
                discount_start_date = %(discount_start_date)s,
                discount_end_date = %(discount_end_date)s,
                min_amount = %(min_amount)s,
                max_amount = %(max_amount)s,
                manufacturer = %(manufacturer)s,
                date_of_manufacture = %(date_of_manufacture)s,
                origin = %(origin)s
            WHERE
                id = %(product_id)s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
    
    def patch_products_history(self, conn, params: dict):
        sql = """
            INSERT INTO product_history (
                product_id,
                modify_account_id,
                is_selling,
                is_displayed,
                title,
                simple_description,
                content,
                price,
                discount_rate,
                discount_start_date,
                discount_end_date,
                min_amount,
                max_amount,
                manufacturer,
                date_of_manufacture,
                origin
            )
            VALUES (
                %(product_id)s,
                %(modify_account_id)s,
                %(is_selling)s,
                %(is_displayed)s,
                %(title)s,
                %(simple_description)s,
                %(content)s,
                %(price)s,
                %(discount_rate)s,
                %(discount_start_date)s,
                %(discount_end_date)s,
                %(min_amount)s,
                %(max_amount)s,
                %(manufacturer)s,
                %(date_of_manufacture)s,
                %(origin)s
            )
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
    
    def get_options_by_product_id(self, conn, product_id: int):
        sql = """
            SELECT
                op.id AS option_id,
                op.color_id,
                op.size_id,
                op.price,
                op.stock
            FROM
                options AS op
            WHERE
                op.product_id = %s
                AND
                op.is_deleted = 0
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, product_id)
            return cursor.fetchall()
    
    def update_option_info(self, conn, update_data: list):
        sql = """
            UPDATE options
            SET
                color_id = %(color_id)s,
                size_id = %(size_id)s,
                price = %(price)s,
                stock = %(stock)s,
                is_deleted = 0
            WHERE 
                product_id = %(product_id)s

        """
        with conn.cursor() as cursor:
            cursor.executemany(sql, update_data)
    
    def update_option_history(self, conn, update_data: list):
        sql = """
            INSERT INTO options_history (
                option_id,
                modify_account_id,
                price,
                is_deleted
            )
            VALUES (
                %(option_id)s,
                %(modify_account_id)s,
                %(price)s,
                0
            )
        """
        with conn.cursor() as cursor:
            cursor.executemany(sql, update_data)
    
    def delete_option_info(self, conn, exist_options: list):
        sql = """
            UPDATE options 
            SET
                is_deleted = 1
            WHERE
                id = %(option_id)s
        """
        with conn.cursor() as cursor:
            cursor.executemany(sql, exist_options)
    
    def delete_option_history(self, conn, exist_options: list):
        sql = """
            INSERT INTO options_history (
                option_id,
                price,
                modify_account_id,
                is_deleted
            )
            VALUES (
                %(option_id)s,
                %(price)s,
                %(modify_account_id)s,
                1
            )
        """
        with conn.cursor() as cursor:
            cursor.executemany(sql, exist_options)
        
    def delete_images_in_product_images(self, conn, params: dict):
        sql = """
            UPDATE product_images
            SET
                is_deleted = %(is_deleted)s,
                deleted_at = %(deleted_at)s
            WHERE
                product_id = %(product_id)s
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, params)