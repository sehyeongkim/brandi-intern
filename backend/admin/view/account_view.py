from datetime import datetime

from flask.views import MethodView
from flask import request, jsonify, g, send_file
from flask_request_validator import Param, Pattern, JSON, validate_params, ValidRequest, GET, Min, Enum, HEADER
from flask_request_validator.error_formatter import demo_error_formatter
from flask_request_validator.exceptions import InvalidRequestError, InvalidHeadersError, RuleError

from utils.custom_exception import DatabaseCloseFail
from utils.response import post_response, get_response
from utils.decorator import LoginRequired
from connection import get_connection
from utils.decorator import LoginRequired


from timeit import repeat

class AccountSignUpView(MethodView):
    def __init__(self, service):
        self.service = service
    # account 회원가입
    # router => class => validate_params
    # rules 최상단에서 에러 처리
    # 최종적인 메시지 처리는 최상단에서
    # 어떤 문제가 있는지 멘트 처리 알아보기

    @validate_params(
        Param('id', JSON, str, rules=[
              Pattern("^[a-z]+[a-z0-9]{4,19}$")], required=True),
        Param('password', JSON, str, rules=[
              Pattern('^[A-Za-z0-9@#!$]{6,12}$')], required=True),
        Param('phone', JSON, str, required=True),
        Param('sub_property_id', JSON, int, required=True),
        Param('korean_brand_name', JSON, str, required=True,
              rules=[Pattern('[가-힣a-zA-Z0-9]+')]),
        Param('english_brand_name', JSON, str, required=True,
              rules=[Pattern('[a-zA-Z0-9]+')]),
        Param('customer_center_number', JSON, str, required=True)
    )
    def post(self, valid: ValidRequest):
        conn = None
        try:
            body = valid.get_json()
            conn = get_connection()
            self.service.post_account_signup(conn, body)
            conn.commit()
            return post_response({"message": "success", "status_code" : 200}), 200
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            try:
                if conn:
                    conn.close()
            except Exception as e:
                raise DatabaseCloseFail('서버에 알 수 없는 오류가 발생했습니다')


class AccountLogInView(MethodView):
    def __init__(self, service):
        self.service = service

    
    @validate_params(
        Param('id', JSON, str, rules=[Pattern("^[a-z]+[a-z0-9@.]{4,19}$")], required=True),
        Param('password', JSON, str, rules=[Pattern('^[A-Za-z0-9@#$]{6,12}$')], required=True)
    )
    def post(self, valid):
        conn = None
        try:
            body = valid.get_json()        
            conn = get_connection()
            # 계정을 먼저 가져와서 처리하는게 더 안전
            if body['id'].find("@") == -1 :
                # Seller 로그인
                result = self.service.post_account_login(conn, body)
            else:
                # Master 로그인
                result = self.service.post_master_login(conn, body)
            
            return post_response({
                        "message" : "success", 
                        "accessToken" : result['accessToken'],
                        "account_type_id" : result['account_type_id'],
                        "status_code" : 200
                        }), 200
        finally:
            try:
                conn.close()
            except Exception as e:
                raise DatabaseCloseFail('서버에 알 수 없는 오류가 발생했습니다.')



class SellerListView(MethodView):
    def __init__(self, service):
        self.service=service

    @LoginRequired("seller")
    @validate_params(
        Param('Content-Type', HEADER, str, required=False),
        Param('id', GET, int, required=False),
        Param('seller_identification', GET, str, required=False),
        Param('english_brand_name', GET, str, required=False),
        Param('korean_brand_name', GET, str, required=False),
        Param('manager_name', GET, str, required=False),
        Param('seller_status_type_id', GET, str, required=False),
        Param('manager_phone', GET, str, required=False),
        Param('manager_email', GET, str, required=False),
        Param('sub_property_id', GET, int, required=False),
        Param('start_date', GET, str, required=False),
        Param('end_date', GET, str, required=False),
        Param('page', GET, int, required=False, default=1, rules=[Min(1)]),
        Param('limit', GET, int, required=False, default=10, rules=[Enum(10, 20, 50)])
    )
    def get(self, valid):
        """셀러 계정 리스트 조회

        Args:
            valid (ValidRequest): parameter로 들어온 값

        Returns:
            seller_list_results (list): 
        """
        conn = None
        try:
            params = valid.get_params()
            headers = valid.get_headers()
            conn=get_connection()
            seller_list_results = self.service.get_seller_list(conn, params, headers)

            if 'application/vnd.ms-excel' in headers.values():
                today = datetime.today().strftime('%Y-%m-%d')
                return send_file(seller_list_results, attachment_filename=f'{today}seller_list.xls', as_attachment=True)

            return get_response(seller_list_results), 200
        finally:
            conn.close()
    
    @LoginRequired("seller")
    def patch(self, seller_id):
        """셀러 계정의 입점 상태 변화

        셀러 계정의 입점 상태를 변화하는 함수(입점신청, 입점, 휴점, 휴점신청 등)

        Raises:
            e: 예상치 못한 에러
            DatabaseCloseFail: 데이터베이스 close에 실패했을 때 발생하는 에러

        Returns:
           get_response (dict) : 성공시 SUCCESS 반환
        """
        conn = None
        try:
            params = request.get_json()
            conn = get_connection()

            params["account_id"] = g.account_id
            params["seller_id"] = seller_id
            params
            self.service.change_seller_status_type(conn, params)

            conn.commit()

            return get_response("SUCCESS")
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            try:
                conn.close()
            except Exception as e:
                raise DatabaseCloseFail('서버에 알 수 없는 오류가 발생했습니다.')


class SellerView(MethodView):
    def __init__(self, service):
        self.service=service
    
    @LoginRequired("seller")
    def get(self, seller_id):
        """셀러 계정 수정을 위한 상세정보

        셀러 계정 수정을 위해 가져오는 상세 정보들을 표출

        Args:
            seller_identification (str): 셀러 아이디

        Raises:
            DatabaseCloseFail: 데이터베이스 close에 실패했을 때 발생하는 에러

        Returns:
            seller_info (dict): 셀러 상세 정보를 표출
        """
        
        conn = None
        try:
            params = dict()
            params["seller_id"] = seller_id
            conn = get_connection()
            seller_info = self.service.get_seller_info(conn, params)

            return get_response(seller_info), 200
        finally:
            try:
                conn.close()
            except Exception as e:
                raise DatabaseCloseFail('서버에 알 수 없는 오류가 발생했습니다.')
    

    @LoginRequired("seller")
    def patch(self, seller_id):
        conn = None
        try:
            params = request.get_json()
            conn = get_connection()
            params["account_id"] = g.account_id
            params["account_type_id"] = g.account_type_id
            params["seller_id"] = seller_id
            manager_params = params["manager_info_list"]
            del params["manager_info_list"]


            # manager id 다 가져오기/ 원래꺼 지우고 다시 하는게 더 나을듯? / 데이터베이스에 더 적게 잇을 때 -> 추가/ 데이터베이스에 더 많을 때 -> 삭제
            for manager_param in manager_params:
                manager_param["account_id"] = g.account_id
                manager_param["seller_id"] = seller_id
            
            self.service.update_seller_info(conn, params, manager_params)

            conn.commit()

            return get_response("SUCCESS")
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            try:
                conn.close()
            except Exception as e:
                raise DatabaseCloseFail('서버에 알 수 없는 오류가 발생했습니다.')
        
