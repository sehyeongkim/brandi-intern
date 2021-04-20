import pymysql

class AccountDao:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def get_userid(self, conn, id):
        sql = """
            SELECT * FROM sellers
            WHERE seller_identification = %s
        """
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, id)
            result = cursor.fetchall()
            return result
    
    def create_account_dao(self, conn, account_type_id):
        sql = """
            INSERT INTO account ( 
                account_type_id 
            ) VALUES (
                %(account_type_id)s
            )
        """
        with conn.cursor() as cursor:
            cursor.execute(sql, account_type_id)
            account_id = cursor.lastrowid
            
            if not account_id:
                return False
            return account_id
    
    def create_seller_signup(self, conn, data):
        pass

    def post_account_login(self, conn, data):
        pass

    # decorator 가 account_id 비교하는 로직
    def decorator_find_account(self, conn, account_id):
        with conn.cursor() as cursor:
            sql = """
                    SELECT
                    *
                    FROM
                    account
                    WHERE
                    id = :account_id
                """
            
            cursor.execute(sql)
            return cursor.fetchone()