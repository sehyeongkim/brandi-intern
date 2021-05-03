import pymysql

from config import DB, AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME, REGION

import boto3

def get_connection():
    return pymysql.connect(
        host=DB["HOST"],
        user=DB["USER"],
        password=DB["PASSWORD"],
        database=DB["DATABASE"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

def get_s3_connection():
    s3_connection = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=REGION,
    )
    return s3_connection