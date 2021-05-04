from datetime import datetime

# order_status
PURCHASE_COMPLETE = 4 # 구매확정
CANCEL_COMPLETE = 7 # 취소완료
REFUND_COMPLETE = 9 # 환불완료


# account_type_id
MASTER = 1
SELLER = 2
USER = 3


# 셀러 계정 상태 
STORE_REJECTED = 3 # 입점 거절
STORE_OUT = 6 # 퇴점


START_DATE = datetime(1111, 1, 1, 0, 0)
END_DATE = datetime(9999, 12, 31, 23, 59)
PRODUCT_INFO_NOTICE = "상품 상세 참조"