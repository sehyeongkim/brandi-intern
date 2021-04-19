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