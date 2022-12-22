from datetime import datetime
from dateutil.parser import parse
from utils.custom_exception import DataTypeDoesNotMatch
def validate_float(value):
    try:
        if isinstance(value, float):
            return value
    except Exception:
        raise DataTypeDoesNotMatch('입력값의 형태가 올바르지 않습니다.')

def validate_integer(value):
    
    if isinstance(value, int):
        try:
            if value < 0:
                raise DataTypeDoesNotMatch('음수값은 입력될 수 없습니다.')

            return value
        
        except Exception:
            raise DataTypeDoesNotMatch('입력값의 형태가 올바르지 않습니다.')

def validate_boolean(value):
    try:
        if isinstance(value, bool):
            return value

    except Exception:
        raise DataTypeDoesNotMatch('입력값의 형태가 올바르지 않습니다.')


def validate_string(value):
    try:
        if isinstance(value, str):
            return value
    except Exception:
        raise DataTypeDoesNotMatch('입력값의 형태가 올바르지 않습니다.')

def validate_datetime(value):
    try:
        result = parse(value)
        return result
    except:
        raise DataTypeDoesNotMatch('날짜와 시간 입력값의 형태가 올바르지 않습니다.')

def validate_date(value):
    try:
        result = parse(value)
        return result
    except:
        raise DataTypeDoesNotMatch('날짜 입력값의 형태가 올바르지 않습니다.')
