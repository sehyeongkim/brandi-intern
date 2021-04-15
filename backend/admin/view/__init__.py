import pymysql


def create_endpoints(app, services):

    app.add_url_rule("/products", view_func=ProductView.as_view(""))
