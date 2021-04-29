import sys
sys.path.insert(1, '../')

from flask import Flask
from flask_cors import CORS
from flask.json import JSONEncoder

from service import (
    ProductService,
    OrderService,
    AccountService
)

from view import create_endpoints

from utils.error_handler import error_handle

class Service:
    pass

def create_app():
    app = Flask(__name__)

    CORS(app)

    services = Service()

    services.product_service = ProductService()
    services.order_service = OrderService()
    services.account_service = AccountService()

    # endpoint 생성
    create_endpoints(app, services)
    
    # app.json_encoder = CustomJSONEncoder
    
    error_handle(app)

    return app