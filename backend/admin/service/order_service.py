from admin.model import OrderDao

from utils.custom_exception import DataNotExists, DatabaseConnectFail, StartDateFail

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
        """주문 조회 리스트 서비스

        주문 리스트 정보를 위해 model로 정보를 넘김
        
        Args:
            conn (Connection): DB 커넥션 객체
            params (dict): query parameter로 받은 정보 (셀러명, 조회 기간 등)
            
        Returns:

        """
        if 'start_date' in params and 'end_date' in params and params['start_date'] > params['end_date']:
                    raise  StartDateFail('조회 시작 날짜가 끝 날짜보다 큽니다.')
        
        result_1, result_2 = self.order_dao.get_order_list(conn, params)
        order_list_info = {
                "order_list" : [
                    {
                        "color_id": result["color_id"],
                        "order_created_at": result["created_at"],
                        "order_detail_number": result["detail_order_number"],
                        "brand_name": result["korean_brand_name"],
                        "order_number": result["order_number"],
                        "order_status_type_id": result["order_status_type_id"],
                        "order_username": result["order_username"],
                        "orderer_phone": result["orderer_phone"],
                        "price": result["price"],
                        "quantity": result["quantity"],
                        "size_id": result["size_id"],
                        "product_name": result["title"]
                    } for result in result_1
                ],
                "total_count": result_2["count"]
        }

        return order_list_info
    
    # order_status_type 변경
    def patch_order_status_type(self, conn, body):
<<<<<<< HEAD
<<<<<<< HEAD
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
=======
        # DB에 없는 주문 상태를 전달할 때 -> dao에서 처리하기 or view 혹은 service에서 처리하기
=======

        appropriate_id = self.order_dao.check_appropriate_order_status_type(conn, body) # order_status_type이 11보다 큰지 확인
        # DB에 order_status_type이 존재하는지 확인
        # 어차피 하나의 버튼을 누르면 바뀌는 것이기 때문에 존재여부만 파악하면 될듯
        if not appropriate_id:
            raise DataNotExists("처리할 수 없는 데이터 값입니다.")

        checked_current_order_status_list = self.order_dao.check_current_order_status(conn, body) 

>>>>>>> [Admin > order]
        # 주문 취소가 된 상품인 경우 -> 수정을 못하도록 에러발생
        # 이미 구매확정이 된 상품인 경우 -> 수정을 못하도록 에러발생
        possible_change_order_status = list()
        not_possible_change_order_status = list()
        for current_order_status_type in checked_current_order_status_list:
            if current_order_status_type["order_status_type_id"] in (4, 6, 9):
                not_possible_change_order_status.append(current_order_status_type)
            else:
                possible_change_order_status.append(current_order_status_type)

        results = list()
        for order_status in possible_change_order_status:
            order_status["order_status_type_id"] = body[0]["order_status_type_id"]

            results.append(order_status)

        self.order_dao.patch_order_status_type(conn, results)
        self.order_dao.insert_order_detail_history(conn, results)


        if not_possible_change_order_status:
            return not_possible_change_order_status

        
    
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
>>>>>>> [Admin > order_dao, order_service, order_view]
