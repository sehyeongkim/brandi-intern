from model import ProductDao

class ProductService:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.product_dao = ProductDao()
    
    # 상품 리스트 가져오기
    def get_products_list(self, conn, params):
        return product_dao.get_products_list(conn, params)
    
    # 상품 등록 (by seller or master)
    def post_product_by_seller_or_master(self, conn, body):
        return product_dao.post_product_by_seller_or_master(conn, body)
    
    # 상품 리스트에서 상품의 판매여부, 진열여부 수정
    def patch_product_selling_or_display_status(self, conn, body):
        return product_dao.patch_product(conn, body)
    
    # 상품 상세 가져오기
    def get_product_detail(self, conn, product_code):
        return product_dao.get_product_detail(conn, product_code)
    
    # 상품 categories list 가져오기
    def get_categories_list(self, conn, category_id):
        return product_dao.get_categories_list(conn, category_id)
    
    # sellers list 가져오기
    def get_sellers_list(self, conn, seller_id):
        return product_dao.get_seller_list(conn, seller_id)

    # 상품 등록 창에서 seller 검색
    def search_seller(self, conn, params):
        return product_dao.search_seller(conn, params)
