from datetime import datetime
from utils.custom_exception import DataTypeDoesNotMatch

# seller_id, property_id, category_id, sub_category_id, color_id, size_id, stock, min_amount, max_amount, price
def validate_integer(value):
    
    if isinstance(value, int):
        try:
            if value < 0:
                raise DataTypeDoesNotMatch('음수값은 입력될 수 없습니다.')

            return value
        
        except Exception:
            raise DataTypeDoesNotMatch('입력값의 형태가 올바르지 않습니다.')

# is_selling, is_displayed
def validate_boolean(value):
    try:
        if value == 0 or value == 1:
            return value
    except Exception:
        raise DataTypeDoesNotMatch('입력값의 형태가 올바르지 않습니다.')

# discount_rate
def validate_float(value):
    try:
        if isinstance(value, float):
            return value
    except Exception:
        raise DataTypeDoesNotMatch('입력값의 형태가 올바르지 않습니다.')

# manafucturer, date_of_manufacture, title, content
def validate_string(value):
    try:
        if isinstance(value, str):
            return value
    except Exception:
        raise DataTypeDoesNotMatch('입력값의 형태가 올바르지 않습니다.')

# discount_start_date, discount_end_date
def validate_datetime(value):
    try:
        dt_obj = datetime.strptime(value, '%Y-%m-%d %H:%M')
        return dt_obj
    
    except ValueError:
        raise DataTypeDoesNotMatch('날짜 입력값의 형태가 올바르지 않습니다.')


# from webargs import fields, validate

# validate_basic_info = {
#     "basic_info": fields.Nested(
#         {
#             "seller_id": fields.Int(validate=validate.Range(min=1), required=True),
#             "is_selling": fields.Bool(required=True),
#             "is_displayed": fields.Bool(required=True),
#             "property_id":fields.Int(validate=validate.Range(min=1), required=True),
#             "category_id":fields.Int(validate=validate.Range(min=1), required=True),
#             # "product_info_notice":fields.Nested(
#             #     {"manufacturer": fields.Str(),
#             #     "date_of_manufacture": fields.Str(),
#             #     "origin": fields.Str()}),
#             "title":fields.Str(required=True),
#             "simple_description":fields.Str(required=False),
#             "content": fields.Str(required=True)
#     })}

# validate_selling_info = {
#     "selling_info": fields.Nested({
#     "price": fields.Int(validate=validate.Range(min=1)),
#     "discount_rate": fields.Float(),
#     "discount_start_date": fields.DateTime("%Y-%m-%d %H:%M:%S"),
#     "discount_end_date": fields.DateTime("%Y-%m-%d %H:%M:%S"),
#     "min_amount": fields.Int(validate=validate.Range(min=1)),
#     "max_amount": fields.Int(validate=validate.Range(max=20))
# })}
