from admin.model import OrderDao

<<<<<<< HEAD
=======

>>>>>>> Order 주문관리 진행중
class OrderService:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance                      

    def __init__(self):
        self.order_dao = OrderDao()
<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> Order 주문관리 진행중
    
>>>>>>> Modify: Directory 구조 변경 및 경로 수정정
    # 주문 조회
    def get_order_list(self, conn, params):
        return self.order_dao.get_order_list(conn, params)
    
    # order_status_type 변경
    def patch_order_status_type(self, conn, body):
<<<<<<< HEAD
<<<<<<< HEAD
        return order_dao.patch_order_status_type(conn, body)
    
    #배송완료, 상품준비, 전체상품, 노출상품
    def get_dashboard_seller(self, conn, account_id):
        return self.order_dao.get_dashboard_seller(conn, account_id)
        
=======
        return self.order_dao.patch_order_status_type(conn, body)
>>>>>>> Modify: Directory 구조 변경 및 경로 수정정
=======
        return self.order_dao.patch_order_status_type(conn, dbody)
>>>>>>> Order 주문관리 진행중
