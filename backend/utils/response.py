def error_response(user_error_message, dev_error_message, status_code=500):
    response = {
                    "user_error_message" : user_error_message,
                    "dev_error_message" : dev_error_message,
                    "status_code": status_code
                }
    return response

def post_response(data, status_code=200):
    """post 요청에 response하는 함수

    Args:
        data (dict): 프론트로 반환할 dict 데이터

    Returns:
        dict : 프론트로 result라는 dict안에 data라는 dict을 반환
    """
    response = {
        "result" : data
    }    
                
    return response

def get_response(result, status_code=200):
    response = {
                    "result" : result,
                    "status_code": status_code
                }
    return response

def post_response_with_return(message, fail_return, status_code=200):
    response = {
                    "message": message,
                    "post_fail": fail_return,
                    "status_code": status_code
                }
    return response
