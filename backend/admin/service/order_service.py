from admin.model import OrderDao


class OrderService:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance                      

    def __init__(self):
        self.order_dao = OrderDao()
    
    # 주문 조회
    def get_order_list(self, conn, params):
        """주문 조회 리스트 서비스

        주문 리스트 정보를 위해 model로 정보를 넘김
        
        Args:
            conn (Connection): DB 커넥션 객체
            params (dict): query parameter로 받은 정보 (셀러명, 조회 기간 등)
            
        Returns:
            self.order_dao.get_order_list(conn, params): order_dao에서 리턴한 값
        """
        return self.order_dao.get_order_list(conn, params)
    
    # order_status_type 변경
    def patch_order_status_type(self, conn, body):
        # DB에 없는 주문 상태를 전달할 때 -> dao에서 처리하기 or view 혹은 service에서 처리하기
        # 주문 취소가 된 상품인 경우 -> 수정을 못하도록 에러발생
        # 이미 구매확정이 된 상품인 경우 -> 수정을 못하도록 에러발생
        return self.order_dao.patch_order_status_type(conn, body)
    
    def get_order(self, conn, params):
        result_1, result_2 = self.order_dao.get_order(conn, params)

        order_detail_info = {
                "order_detail": {
                    "order_number": result_1["order_number"],
                    "order_detail_number": result_1["detail_order_number"],
                    "order_created_at": result_1["created_at"],
                    "order_status_type_id": result_1["order_status_type_id"],
                    "orderer_phone": result_1["order_phone"],
                    "product_id": result_1["product_id"],
                    "option_id": result_1["option_id"],
                    "price": result_1["price"],
                    "discount_rate": result_1["discount_rate"],
                    "discount_start_date": result_1["discount_start_date"],
                    "discount_end_date": result_1["discount_end_date"],
                    "product_name": result_1["title"],
                    "brand_name": result_1["korean_brand_name"],
                    "color_id": result_1["color_id"],
                    "size_id": result_1["size_id"],
                    "quantity": result_1["quantity"],
                    "user_id": result_1["user_id"],
                    "recipient": result_1["recipient"],
                    "zip_code": result_1["zip_code"],
                    "address": result_1["address"]+" "+result_1["detail_address"],
                    "recipient_phone": result_1["recipient_phone"],
                    "delivery_memo": result_1["delivery_memo_custom"] if result_1["delivery_memo_custom"] else result_1["delivery_memo"] if result_1["delivery_memo"] else None,
                },
                "order_history": [
                            {
                                "update_time": result["updated_at"],
                                "order_status_type": result["order_status_type_id"]
                            }
                            for result in result_2
                        ]
        }
        return order_detail_info