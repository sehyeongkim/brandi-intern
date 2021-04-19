from model import OrderDao

order_dao = OrderDao()
class OrderService:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance                      

    def __init__(self):
        pass
    
    # 주문 조회
    def get_order_list(self, conn, params):
        return order_dao.get_order_list(conn, params)
    
    # order_status_type 변경
    def patch_order_status_type(self, conn, body):
        return order_dao.patch_order_status_type(conn, dbody)