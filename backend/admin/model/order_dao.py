class OrderDao:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass
    
    def get_order_list(self, conn, params):
        pass

    def patch_order_status_type(self, conn, body):
        pass

    def get_dashboard_seller(self, conn, account_id):
        #전체상품, 노출상품
        sql1 = """
                SELECT
                    COUNT(*) AS product_all,
                    COUNT(case when is_selling=1 then 1 end) AS product_selling
                FROM
                    account AS ac
                INNER JOIN sellers AS se
                    ON ac.id = se.account_id
                INNER JOIN products AS pr
                    ON se.id = pr.seller_id
                WHERE pr.seller_id = %(account_id)s;
                """
        # 상품준비, 배송완료
        sql2 =  """
                SELECT 
                    COUNT(case when od.order_status_type_id=1 then 1 end) AS before_delivery,
                    COUNT(case when od.order_status_type_id=3 then 1 end) AS complete_delivery
                FROM account AS ac
                INNER JOIN sellers AS se
                    ON ac.id = se.account_id
                INNER JOIN products AS pr
                    ON se.id = pr.seller_id
                INNER JOIN orders_detail AS od
                    ON pr.id = od.product_id
                WHERE pr.seller_id = %(account_id)s;
                """
        #30일간 결제건수, 결제금액
        sql3 = """
                SELECT 
                    COUNT(case when oh.order_status_type_id=11 then 1 end) AS order_month,
                    SUM(od.price*od.quantity) AS price_month
                FROM account AS ac
                INNER JOIN sellers AS se
                    ON ac.id = se.account_id
                INNER JOIN products AS pr
                    ON se.id = pr.seller_id
                INNER JOIN orders_detail AS od
                    ON pr.id = od.product_id
                INNER JOIN order_detail_history AS oh
                		ON oh.order_detail_id = od.id
                WHERE pr.seller_id = %(account_id)s AND oh.updated_at BETWEEN DATE_ADD(NOW(),INTERVAL -1 MONTH ) AND NOW();
                """
            
        params = dict()
        params['account_id'] = account_id

        with conn.cursor() as cursor:
            cursor.execute(sql1, params)
            result1 = cursor.fetchall()
            print(result1,'===============================')

            cursor.execute(sql2 , params)
            result2 = cursor.fetchall()
            print(result2,'===============================')

            cursor.execute(sql3, params)
            result3 = cursor.fetchall()
            print(result3,'===============================')

            return result1, result2, result3

       