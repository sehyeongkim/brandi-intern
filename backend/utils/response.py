def error_response(user_error_message, dev_error_message, status_code=500):
    response = {
                    "user_error_message" : user_error_message,
                    "dev_error_message" : dev_error_message,
                    "status_code": status_code
                }
    return response

def post_response(message, status_code=200):
    response = {
                    "message": message,
                    "status_code": status_code
                }
    return response

def get_response(results, status_code=200):
    response = {
                    "results" : results,
                    "status_code": status_code
                }
    return response



