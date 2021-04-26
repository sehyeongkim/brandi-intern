from admin.model import OrderDao

from utils.response import error_response
from utils.custom_exception import DataNotExists, DatabaseConnectFail, StartDateFail

import traceback
from datetime import timedelta, date

class OrderService:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance                      

    def __init__(self):
        self.order_dao = OrderDao()
    
    def get_order_list(self, conn, params):
        """주문 조회 리스트 서비스

        주문 리스트 정보를 위해 model로 정보를 넘김
        
        Args:
            conn (Connection): DB 커넥션 객체
            params (dict): query parameter로 받은 정보 (셀러명, 조회 기간 등)
            
        Returns:
            dict : 
                    order_list_info: 
                            order_list_info = {
                                    "order_list" : [
                                        {
                                            "color_id": 색상 아이디,
                                            "order_created_at": 주문 생성 날짜,
                                            "order_detail_number": 주문 상세 번호,
                                            "brand_name": 브랜드명,
                                            "order_number": 주문 번호,
                                            "order_status_type_id": 주문 상태 아이디,
                                            "order_username": 주문자명,
                                            "orderer_phone": 주문자 전화번호,
                                            "price": 상품 가격,
                                            "quantity": 구매 수량,
                                            "size_id": 사이즈 아이디,
                                            "product_name": 상품명
                                        } for result in result_1
                                    ],
                                    "total_count": 주문 전체 수
                            }     
            500 : Exceptions  
                DatabaseConnectFail : DB와의 커넥션이 존재하지 않을 경우 발생하는 에러
                StartDateFail : 조회 날짜가 알맞지 않을 때 발생하는 에러
                KeyError : 데이터베이스의 key값이 맞지 않을 때 발생하는 에러
        """
        
        if 'end_date' in params:
            params['end_date'] +=  timedelta(days=1)
            params['end_date_str'] = params['end_date'].strftime('%Y-%m-%d')

        if 'start_date' in params:
            params['start_date_str'] = params['start_date'].strftime('%Y-%m-%d')

        if 'start_date' in params and 'end_date' in params and params['start_date'] > params['end_date']:
            raise StartDateFail('조회 시작 날짜가 끝 날짜보다 큽니다.')

        orders_info, order_count = self.order_dao.get_order_list(conn, params)
        
        order_list_info = {
                "order_list" : [
                    {
                        "color": result["color_name"],
                        "order_created_at": result["created_at"],
                        "order_detail_number": result["detail_order_number"],
                        "brand_name": result["korean_brand_name"],
                        "order_number": result["order_number"],
                        "order_status_type": result["order_status_type"],
                        "order_username": result["order_username"],
                        "orderer_phone": result["orderer_phone"],
                        "quantity": result["quantity"],
                        "size": result["size_name"],
                        "product_name": result["title"],
                        "total_price": int(result["price"] * result["quantity"]) if result["discount_rate"] == 0 else int(result["price"] * (1-result["discount_rate"]) * result["quantity"])
                    } for result in orders_info # 이름
                ],
                "total_count": order_count["count"]
        }
    
        return order_list_info


    def patch_order_status_type(self, conn, body):
        """주문 및 배송처리 함수

        json으로 받은 값을 바탕으로 주문 및 배송 처리하기 위한 함수

        Args:
            conn (Connection): DB 커넥션 객체
            body (json): 
                [
                    {"orders_detail_id" : 주문 상세 아이디, "order_status_type_id": 변경할 주문 상태 아이디},
                    {"orders_detail_id" : 주문 상세 아이디, "order_status_type_id": 변경할 주문 상태 아이디},
                    {"orders_detail_id" : 주문 상세 아이디, "order_status_type_id": 변경할 주문 상태 아이디}
                    ...
                ]

        Raises:
            DataNotExists: DB에 해당 id가 존재하지 않을 때 발생하는 에러

        Returns:
            list : 주문 상태를 변경하는데 실패한 값 반환
        """
        status_type_exist, status_type_not_exist = self.order_dao.check_if_status_type_exists(conn, body)

        possible_to_patch, impossible_to_patch = self.order_dao.check_if_possible_change(conn, status_type_exist)

        possible_to_patch += status_type_exist
        impossible_to_patch += status_type_not_exist

        self.order_dao.patch_order_status_type(conn, possible_to_patch)
        # self.order_dao.insert_order_detail_history(conn, possible_to_patch)
        return impossible_to_patch
    
        


        
    def get_order(self, conn, params):
        """주문 상세

        주문 상세 정보를 가져오는 함수

        Args:
            conn (Connection): DB 커넥션 객체
            params (dict): {"detail_order_number" : 주문 상세 번호}

        Returns:
            dict : 주문 상세 정보 반환
        """
        result_1, result_2 = self.order_dao.get_order(conn, params)

        order_detail_info = {
                "order_detail": {
                    "order_number": result_1["order_number"],
                    "order_detail_number": result_1["detail_order_number"],
                    "order_created_at": result_1["created_at"],
                    "order_status_type": result_1["order_status_type"],
                    "orderer_phone": result_1["order_phone"],
                    "orderer_name": result_1["orderer_name"],
                    "product_id": result_1["product_id"],
                    "price": result_1["price"],
                    "discount_rate": int(100 * result_1["discount_rate"]),
                    "discounted_price": int(result_1["price"] if result_1["discount_rate"] == 0 else (result_1["price"] * (1-result_1["discount_rate"]))),
                    "total_price": int(result_1["price"] * result_1["quantity"] if result_1["discount_rate"] == 0 else result_1["price"] * result_1["discount_rate"] * result_1["quantity"]),
                    "product_name": result_1["title"],
                    "brand_name": result_1["korean_brand_name"],
                    "color": result_1["color"],
                    "size": result_1["size"],
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
                                "order_status_type": result["order_status_type"]
                            }
                            for result in result_2
                        ]
        }
        return order_detail_info