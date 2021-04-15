import config
from connection import get_connection

from flask import Flask
from flask_cors import CORS


def create_app(test_config=None):
    app = Flask(__name__)

    CORS(app)

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)

    return app


# @app.route("/select", methods=["GET"])
# def select():
#     connection = None
#     try:
#         # 파라메터 벨리데이션
#         # 요청 값 벨리데이션
#         connection = get_connection()
#         # 비지니스 체크
#         with connection.cursor() as cursor:
#             sql = "SELECT * FROM test;"
#             cursor.execute(sql)
#             result = cursor.fetchall()
#             print(result)

#     finally:
#         if connection:
#             connection.close()

#     return result[0]


# @app.route("/insert", methods=["POST"])
# def insert():
#     connection = None
#     try:
#         connection = get_connection()

#         with connection.cursor() as cursor:
#             sql = "INSERT INTO test(name) VALUES ('찬호');"
#             cursor.execute(sql)

#         connection.commit()

#     finally:
#         if connection:
#             connection.close()

#     return "haha"