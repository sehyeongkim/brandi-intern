from flask.json import JSONEncoder
from decimal import Decimal
import datetime, json

"""JSON format 변환하는 기능입니다.
    serialize가 불가능한 테이터 타입을 변환하거나,
    특정 데이터 타입을 원하는 json response 형태로 변환합니다.
"""
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        """if문을 추가하여 원하는 형태로 변환합니다.
            isinstance 는 수정할 수 없습니다.
            지정되지 않은 타입은 JSONEncoder로 인코딩하여 reuturn.
        Args:
            obj : 임의의 parameter.
            두번째 parameter: 변환 할 데이터 타입.

        Returns:
            원하는데이터 타입, 혹은 원하는 response 형태
        """
        if isinstance(obj, Decimal):
            return float(obj)

        if isinstance(obj, datetime.datetime):
           return obj.strftime('%Y-%m-%d %I:%M:%S')

        return JSONEncoder.default(self, obj)