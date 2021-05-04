from admin.model import OrderDao

from utils.response import error_response
from utils.custom_exception import DataNotExists, StartDateFail
from utils.constant import PURCHASE_COMPLETE, CANCEL_COMPLETE, REFUND_COMPLETE

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
            order_list_info (dict) : 
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
                                } for order in order_detail
                            ],
                            "total_count": 주문 전체 수
                        }     
            500 : Exceptions  
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
                        "color": order["color_name"],
                        "orders_detail_id": order["orders_detail_id"],
                        "order_created_at": order["created_at"],
                        "order_detail_number": order["detail_order_number"],
                        "brand_name": order["korean_brand_name"],
                        "order_number": order["order_number"],
                        "order_status_type": order["order_status_type"],
                        "order_username": order["order_username"],
                        "orderer_phone": order["orderer_phone"],
                        "quantity": order["quantity"],
                        "size": order["size_name"],
                        "product_name": order["title"],
                        "total_price": int(order["price"] * order["quantity"]) if order["discount_rate"] == 0 else int(order["price"] * (1-order["discount_rate"]) * order["quantity"])
                    } for order in orders_info 
                ],
                "total_count": order_count["count"]
        }
    
        return order_list_info


    def patch_order_status_type(self, conn, params):
        """주문 및 배송처리 함수

        json으로 받은 값을 바탕으로 주문 및 배송 처리하기 위한 함수

        Args:
            conn (Connection): DB 커넥션 객체
            params (json): 
                [
                    {"orders_detail_id" : 주문 상세 아이디, "order_status_type_id": 변경할 주문 상태 아이디},
                    {"orders_detail_id" : 주문 상세 아이디, "order_status_type_id": 변경할 주문 상태 아이디},
                    {"orders_detail_id" : 주문 상세 아이디, "order_status_type_id": 변경할 주문 상태 아이디}
                    ...
                ]

        Raises:
            DataNotExists: DB에 해당 id가 존재하지 않을 때 발생하는 에러

        Returns:
            impossible_to_patch (list) : 주문 상태를 변경하는데 실패한 값 반환
        """

        # 요청된 주문 상태 중 유효한 값을 넣는 리스트
        match_status_types = list()
        # 요청된 주문 상태 중 유효하지 않은 값을 넣는 리스트
        not_match_status_types = list()
        # 요청된 변경할 주문 상태값이 유효한가 확인하기 위해 DB에서 모든 row를 가져온다.
        order_status_types = self.order_dao.get_status_type(conn)

        # for문을 돌면서 DB에 있는 값이 들어왔는지 확인
        for data in params:
            match_status = list(filter(lambda d: d.get('id') == data.get('order_status_type_id'), order_status_types))
            if match_status:
                match_status_types.append(data)
            else:
                not_match_status_types.append(data)

        # 현재 데이터의 order_status_type_id가 무엇인지 확인
        order_detail_results = self.order_dao.check_if_possible_change(conn, match_status_types)
        
        # DB에 존재하면서, 바꿀 수 있는 값인지 확인
        possible_to_patch = list()
        impossible_to_patch = list()
        for db_data in order_detail_results:
            for rq_data in match_status_types:
                if rq_data.get('orders_detail_id') == db_data.get('orders_detail_id') and db_data["order_status_type_id"] in (PURCHASE_COMPLETE, CANCEL_COMPLETE, REFUND_COMPLETE):
                    impossible_to_patch.append(rq_data)
                    # 바꿀 수 없는 row를 만나면 break로 현재 for문을 빠져나간다.
                    break
                if rq_data.get('orders_detail_id') == db_data.get('orders_detail_id'):
                    possible_to_patch.append(rq_data)

        # 변경 요청 데이터가 유효하지 않은 정보들이 있는 리스트
        impossible_to_patch += not_match_status_types

        # 들어온 요청 값과 possible_to_patch_id와 비교하여 patch
        self.order_dao.patch_order_status_type(conn, possible_to_patch)
        self.order_dao.insert_order_detail_history(conn, possible_to_patch)

        return impossible_to_patch
    
 
    def get_order(self, conn, params):
        """주문 상세

        주문 상세 정보를 가져오는 함수

        Args:
            conn (Connection): DB 커넥션 객체
            params (dict): {"detail_order_number" : 주문 상세 번호}

        Returns:
            order_detail_info (dict) :         
                    order_detail_info = {
                        "order_detail": {
                            "order_number": 주문번호,
                            "order_detail_number": 주문상세번호,
                            "order_created_at": 주문발생 시간,
                            "order_status_type": 주문 상태,
                            "orderer_phone": 주문자 전화번호,
                            "orderer_name": 주문자명,
                            "product_id": 상품번호,
                            "price": 상품가격,
                            "discount_rate": 할인율,
                            "discounted_price": 할인된 가격,
                            "total_price": 총가격,
                            "product_name": 상품명,
                            "brand_name": 브랜드명,
                            "color": 색깔,
                            "size": 크기,
                            "quantity": 구매 수량,
                            "user_id": 사용자 id,
                            "recipient": 수령자명,
                            "zip_code": 우편번호,
                            "address": 주소 및 상세주소,
                            "recipient_phone": 수령자 전화번호,
                            "delivery_memo": 배송시 요청사항,
                        },
                        "order_history": [
                                    {
                                        "update_time": 수정시간,
                                        "order_status_type": 주문 상태 타입
                                    }
                                    for history in order_histories
                                ]
                }
        """
        order_detail, order_histories = self.order_dao.get_order(conn, params)

        order_detail_info = {
                "order_detail": {
                    "order_number": order_detail["order_number"],
                    "order_detail_number": order_detail["detail_order_number"],
                    "order_created_at": order_detail["created_at"],
                    "order_status_type": order_detail["order_status_type"],
                    "orderer_phone": order_detail["order_phone"],
                    "orderer_name": order_detail["orderer_name"],
                    "product_id": order_detail["product_id"],
                    "price": order_detail["price"],
                    "discount_rate": int(100 * order_detail["discount_rate"]),
                    "discounted_price": int(order_detail["price"] if order_detail["discount_rate"] == 0 else (order_detail["price"] * (1-order_detail["discount_rate"]))),
                    "total_price": int(order_detail["price"] * order_detail["quantity"] if order_detail["discount_rate"] == 0 else order_detail["price"] * (1-order_detail["discount_rate"]) * order_detail["quantity"]),
                    "product_name": order_detail["title"],
                    "brand_name": order_detail["korean_brand_name"],
                    "color": order_detail["color"],
                    "size": order_detail["size"],
                    "quantity": order_detail["quantity"],
                    "user_id": order_detail["user_id"],
                    "recipient": order_detail["recipient"],
                    "zip_code": order_detail["zip_code"],
                    "address": order_detail["address"]+" "+order_detail["detail_address"],
                    "recipient_phone": order_detail["recipient_phone"],
                    "delivery_memo": order_detail["delivery_memo_custom"] if order_detail["delivery_memo_custom"] else order_detail["delivery_memo"] if order_detail["delivery_memo"] else None,
                },
                "order_history": [
                            {
                                "update_time": history["updated_at"],
                                "order_status_type": history["order_status_type"]
                            }
                            for history in order_histories
                        ]
        }
        return order_detail_info

    def get_dashboard_seller(self, conn, account_id):
        """ 
            seller의 dashboard data

        Args:
         conn (Connection): DB 커넥션 객체            
         account_id ([int]): 로그인 계정 id

        Returns:
            "result": {
                "before_delivery": 준비중인 상품 수,
                "complete_delivery": 배송된 상품 수,
                "order_month": 30일간 주문 횟수,
                "product_all": 업로드 된 상품 수,
                "product_selling": 현재 판매중인 상품 수,
                "sales_month": 30일 간 결제금액
            },
            "status_code": status code
        """
        return self.order_dao.get_dashboard_seller(conn, account_id)
