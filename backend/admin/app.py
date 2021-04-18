import config

from flask import Flask
from flask_cors import CORS

from service import (
                        ProductService, 
                        OrderService, 
                        AccountService
)
from model import (
                    ProductDao, 
                    OrderDao, 
                    AccountDao
)


def create_app(test_config=None):
    app = Flask(__name__)

    CORS(app)

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)

    # model
    product_dao = ProductDao()
    order_dao = OrderDao()
    account_dao = AccountDao()

    # service
    product_service = ProductService(product_dao)
    order_service = OrderService(order_dao)
    account_service = AccountService(account_dao)

    services = {
        'product_service': product_service,
        'order_service': order_service,
        'account_service': account_service
    }
    
    # endpoint 생성 
    create_endpoints(app, services)
    
    return app
