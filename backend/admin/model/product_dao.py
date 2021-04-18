class ProductDao:
    def get_products_list(self, conn, *args):
        # cursor example
        sql = " SELECT * FROM products"
        with conn.cursor() as cursor:
            result = cursor.execute(sql).fetchall()
        
        return result

    def post_product_by_seller_or_master(self, conn, data):
        pass

    def patch_product_selling_or_display_status(self, conn, data):
        pass

    def get_product_detail(self, conn, product_code):
        pass
    
    def get_categories_list(self, conn, category_id):
        pass

    def get_sellers_list(self, conn, seller_id):
        pass

    def search_seller(self, conn, params):
        pass