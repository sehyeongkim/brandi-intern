from flask import Flask
from flask_cors import CORS
from flask.json import JSONEncoder

from admin.service import (
    ProductService,
    OrderService,
    AccountService
)

from admin.view import create_endpoints

from utils.error_handler import error_handle

class Service:
    pass

def create_app(test_config=None):
    app = Flask(__name__)

    CORS(app)

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)
  
    services = Service()

    services.product_service = ProductService()
    services.order_service = OrderService()
    services.account_service = AccountService()

    # endpoint 생성
    create_endpoints(app, services)

    app.json_encoder = CustomJSONEncoder
    
    error_handle(app)

    return app