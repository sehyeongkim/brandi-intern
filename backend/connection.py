import pymysql

from config import DB

def get_connection():
    return pymysql.connect(
        host=DB["HOST"],
        user=DB["USER"],
        password=DB["PASSWORD"],
        database=DB["DATABASE"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )