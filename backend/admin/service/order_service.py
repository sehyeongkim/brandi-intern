class OrderService:
    def __init__(self, order_dao):
        self.order_dao = order_dao
    
    def get_order_list(self, conn, params):
        return self.order_dao.get_order_list(conn, params)
    
    def patch_order_status_type(self, conn, data):
        return self.patch_order_status_type(conn, data)