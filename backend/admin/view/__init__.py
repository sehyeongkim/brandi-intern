from admin.view.product_view import (
                            ProductView, 
                            ProductDetailView, 
                            ProductSubCategoryView,
                            ProductSellerView,
                            ProductSellerSearchView,
                            ProductColorView,
                            ProductSizeView,
                            ProductContentImageView
)

from admin.view.order_view import (
                            DashboardSellerView,
                            OrderListView,
                            OrderView
)

from admin.view.account_view import (
                            AccountSignUpView,
                            AccountLogInView,
                            SellerListView,
                            SellerView,
                            AccountImageView
)

from utils.error_handler import error_handle


def create_endpoints(app, services):
    product_service = services.product_service
    order_service = services.order_service
    account_service = services.account_service


    # product
    app.add_url_rule("/products",
                    view_func=ProductView.as_view('product_view', product_service), 
                    methods=['GET', 'POST', 'PATCH'])

    app.add_url_rule("/products/<product_code>", 
                    view_func=ProductDetailView.as_view('product_detail_view', product_service), 
                    methods=['GET', 'PATCH'])

    app.add_url_rule("/products/seller", 
                    view_func=ProductSellerSearchView.as_view('product_seller_search_view', product_service), 
                    methods=['GET'])

    app.add_url_rule("/products/seller/<int:seller_id>",
                    view_func=ProductSellerView.as_view('product_seller_view', product_service),
                    methods=['GET'])
    
    app.add_url_rule("/products/subcategory/<int:category_id>", 
                    view_func=ProductSubCategoryView.as_view('product_sub_category_view', product_service), 
                    methods=['GET'])

    app.add_url_rule("/products/color",
                    view_func=ProductColorView.as_view('product_color_view', product_service),
                    methods=['GET'])
    
    app.add_url_rule("/products/size",
                    view_func=ProductSizeView.as_view('product_size_view', product_service),
                    methods=['GET'])

    app.add_url_rule("/products/image",
                    view_func=ProductContentImageView.as_view('product_content_image_view', product_service),
                    methods=['POST'])

    # order
    app.add_url_rule("/orders",
                    view_func=OrderListView.as_view('order_list_view', order_service),
                    methods=['GET'])
    
    app.add_url_rule("/orders",
                    view_func=OrderListView.as_view('order_delivery_view', order_service),
                    methods=['PATCH'])
    
    app.add_url_rule("/orders/<int:order_detail_number>",
                    view_func=OrderView.as_view('order_view', order_service),
                    methods=['GET'])
    
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
    
    app.add_url_rule("/seller/signin",
                    view_func=AccountLogInView.as_view('seller_login_view', account_service),
                    methods=['POST'])
    
    app.add_url_rule("/sellers",
                    view_func=SellerListView.as_view('seller_list_view', account_service),
                    methods=['GET'])

    # /sellers/<int:seller_id>/status
    app.add_url_rule("/sellers/<int:seller_id>",
                    view_func=SellerListView.as_view('seller_update_status_view', account_service),
                    methods=["PATCH"]
                    )
    
    app.add_url_rule("/sellers/<int:seller_id>",
                    view_func=SellerView.as_view('seller_view', account_service),
                    methods=["GET"])
    
    # /sellers/<int:seller_id>
    app.add_url_rule("/sellers/<int:seller_id>/management",
                    view_func=SellerView.as_view('seller_update_view', account_service),
                    methods=["PATCH"])
    
    app.add_url_rule("/sellers/<int:seller_id>/image",
                    view_func=AccountImageView.as_view('seller_image_view', account_service),
                    methods=["PATCH"])
    
    error_handle(app)
