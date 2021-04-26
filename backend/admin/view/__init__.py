from .product_view import (
                            ProductView, 
                            ProductDetailView, 
                            ProductCategoryView,
                            ProductSellerView,
                            ProductSellerSearchView,
                            
)

from .order_view import (
                            OrderView,
                            DashboardSellerView
)

from .account_view import (
                            AccountSignUpView,
                            AccountLogInView
)

def create_endpoints(app, services):

    product_service = services.product_service
    order_service = services.order_service
    account_service = services.account_service
    
    # product
    app.add_url_rule("/products",
                    view_func=ProductView.as_view('product_view', product_service), 
                    methods=['GET','POST', 'PATCH'])

    app.add_url_rule("/products/<product_code>", 
                    view_func=ProductDetailView.as_view('product_detail_view', product_service), 
                    methods=['GET'])

    app.add_url_rule("/products/seller/<int:category_id>", 
                    view_func=ProductCategoryView.as_view('product_category_view', product_service), 
                    methods=['GET'])

    app.add_url_rule("/products/seller/<int:seller_id>",
                    view_func=ProductSellerView.as_view('product_seller_view', product_service),
                    methods=['GET'])

    app.add_url_rule("/products/seller", 
                    view_func=ProductSellerSearchView.as_view('product_seller_search_view', product_service), 
                    methods=['GET'])

    # order
    app.add_url_rule("/order",
                    view_func=OrderView.as_view('order_view', order_service),
                    methods=['GET'])
    
    app.add_url_rule("/order/delivery",
                    view_func=OrderView.as_view('order_delivery_view', order_service),
                    methods=['PATCH'])

    app.add_url_rule("/dashboard/seller",
                    view_func=DashboardSellerView.as_view('dashboard_seller', order_service),
                    methods=['GET'])
    
    # account
    app.add_url_rule("/account/signup",
                    view_func=AccountSignUpView.as_view('account_signup_view', account_service),
                    methods=['POST'])
    
    app.add_url_rule("/account/login",
                    view_func=AccountLogInView.as_view('account_login_view', account_service),
                    methods=['POST'])