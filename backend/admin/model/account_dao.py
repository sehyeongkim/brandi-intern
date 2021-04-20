class AccountDao:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def post_account_signup(self, conn, body):
        pass

    def post_account_login(self, conn, body):
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