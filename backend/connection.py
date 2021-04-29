import pymysql
from boto3 import client
from botocore.exceptions import ClientError

from config import DB, AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME, REGION

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
    try:
        result = client('s3',
                        aws_access_key_id = AWS_ACCESS_KEY, 
                        aws_secret_access_key = AWS_SECRET_KEY
                        )
        
        return result

    except ClientError as e:
        return "ClientError"
