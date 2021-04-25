from config import BUCKET_NAME
from connection import get_s3_connection

# ISSUE -------> file 하나만 upload 하려고 한다면? files를 args 로 받는게 나을 것 같은디

def upload_image_file(bucket: str, files: list, object_name=None):
    
    if object_name is None:
        object_name = file_name

    try:
        s3_conn = get_s3_connection()
        location = ""
        result = []

        for file in files:
            s3_conn.upload_file(file, bucket, object_name)
            image_url = "https://{BUCKET_NAME}.s3.{location}/{file}"
            result.append(image_url)
        
        return result

    finally:
        pass


if __name__="__main__":
    upload_image_file()