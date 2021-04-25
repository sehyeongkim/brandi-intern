import random, string

from admin.model import ProductDao

from config import BUCKET_NAME, LOCATION

from connection import get_s3_connection

from utils.custom_exception import RequiredDataError

class ProductService:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.product_dao = ProductDao()
    
    # 상품 리스트 가져오기
    def get_products_list(self, conn, params):
        return self.product_dao.get_products_list(conn, params)
    
    # 상품 등록 by seller or master
    def create_basic_info(self, conn, basic_info: dict):

        product_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
        basic_info['product_code'] = product_code            

        return self.product_dao.create_basic_info_dao(conn, basic_info)

    def create_selling_info(self, conn, selling_info: dict):
        return self.product_dao.create_selling_info_dao(conn, selling_info)

    def create_option_info(self, conn, product_id:int, option_info: list):

        for option in option_info:
            option_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=25))
            option['option_code'] = option_code
            option['product_id'] = product_id

        return self.product_dao.create_option_info_dao(conn, option_info)

    # s3에 이미지 파일 업로드
    def upload_file_to_s3(bucket: str, file_name: str, object_name=None):

        if object_name is None:
            object_name = file_name
    
        s3_conn = get_s3_connection()
        s3_conn.upload_file(file_name, bucket, object_name)

        image_url = "https://{BUCKET_NAME}.s3.{LOCATION}.amazonaws.com/{file_name}"
        
        return image_url
    
    def create_image_url(self, conn, product_id: int, files: list):

        # files = ['IMAGE_646.JPG', 'IMG_8954.JPG', 'IMG_6344.JPG']
        # 대표이미지 없을 때 오류
        images = [upload_file_to_s3(BUCKET_NAME, file_name) for file_name in files]

        return self.product_dao.create_image_url_dao(conn, product_id, images)

    # 상품 리스트에서 상품의 판매여부, 진열여부 수정
    def patch_product_selling_or_display_status(self, conn, body):
        return self.product_dao.patch_product(conn, body)
    
    # 상품 상세 가져오기
    def get_product_detail(self, conn, product_code):
        return self.product_dao.get_product_detail(conn, product_code)
    
    # 상품 등록 창에서 seller 검색 master만 가능함
    def search_seller(self, conn, keyword:str):
        keyword = keyword + '%'
        return self.product_dao.search_seller_dao(conn, keyword)
    
    # seller 속성, 1차 카테고리
    def get_property_and_available_categories_list(self, conn, seller_id: int):
        return self.product_dao.get_property_and_available_categories_list_dao(conn, seller_id)
    
    # 상품 categories list 가져오기
    def get_sub_categories_list(self, conn, category_id: int):
        return self.product_dao.get_sub_categories_list_dao(conn, category_id)
    
    # 상품 등록 창에서 color list 뿌려주기
    def get_products_color_list(self, conn):
        """ 상품 등록 창에서 색상 리스트 출력

        색상 등록시 선택 가능한 색상 리스트 출력값의 각 id의 key값을
        id -> color_id 로 변경

        Args:
            conn (pymysql.connections.Connection): DataBase Connection Object

        Returns:
            List: [ {'color_id': 1, 'name': 'red'}, {'color_id': 2, 'name': 'black'}, ...]
        """
        color_info = self.product_dao.get_products_color_list_dao(conn)
        
        for info in color_info:
            info['color_id'] = info.pop('id')
        
        return color_info


    # 상품 등록 창에서 size list 뿌려주기
    def get_products_size_list(self, conn):
        """ 상품 등록 창에서 사이즈 리스트 출력

        사이즈 등록시 선택 가능한 사이즈 리스트 출력값의 각 id의 key값을
        id -> size_id 로 변경

        Args:
            conn (pymysql.connections.Connection): DataBase Connection Object

        Returns:
            List: [ {'size_id': 1, 'name': 's'}, {'size_id': 2, 'name': 'm'}, ...]
        """
        size_info = self.product_dao.get_products_size_list_dao(conn)
        
        for info in size_info:
            info['size_id'] = info.pop('id')

        return size_info