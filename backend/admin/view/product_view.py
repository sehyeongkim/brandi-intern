import xlwt
import json
from ast import literal_eval
from datetime import datetime
from flask import request, jsonify, g, send_file
from flask.views import MethodView
from flask_request_validator import validate_params, Param, GET, Datetime, ValidRequest, CompositeRule, Min, Max, Enum, JsonParam, JSON, HEADER, PATH
from flask_request_validator.exceptions import InvalidRequestError, RulesError

from utils.response import get_response, post_response, post_response_with_return, post_response_success
from utils.decorator import LoginRequired
from utils.custom_exception import (
                                        IsInt, 
                                        IsStr, 
                                        IsFloat,
                                        IsBool, 
                                        IsRequired, 
                                        DatabaseCloseFail, 
                                        RequiredDataError, 
                                        DatabaseRollBackError,
                                        SellerBrandNameDoesNotExist,
                                        UploadFailtoS3,
                                        DataCannotBeConverted
)

from connection import get_connection

class ProductView(MethodView):
    def __init__(self, service):
        self.service = service

    @validate_params(
        Param('Content-Type', HEADER, str, required=False),
        Param('Authorization', HEADER, str, required=False),
        Param('selling', GET, int, required=False),
        Param('discount', GET, int, required=False),
        Param('start_date', GET, str, required=False),
        Param('end_date', GET, str, required=False),
        Param('displayed', GET, str, required=False),
        Param('sub_property', GET, list, required=False),
        Param('seller', GET, str, required=False),
        Param('product_name', GET, str, required=False),
        Param('product_code', GET, str, required=False),
        Param('product_number', GET, int, required=False),
        Param('page', GET, int, required=False, default=1, rules=[Min(1)]),
        Param('limit', GET, int, required=False, default=10, rules=[Enum(10, 20, 50)]),
        Param('start_date', GET, str, rules=[Datetime('%Y-%m-%d')], required=False),
        Param('end_date', GET, str, rules=[Datetime('%Y-%m-%d')], required=False),
        Param('select_product_id', GET, list, required=False)
    )
    # @LoginRequired('seller')
    def get(self, valid: ValidRequest):
        """상품 조회 리스트

        어드민 페이지의 상품관리 페이지에서 필터 조건에 맞는 주문 리스트가 출력됨.

        Args:
            conn (pymysql.connections.Connection): DB 커넥션 객체
            params (dict): 상품번호, 상품명, 상품코드, 판매여부, 진열여부 등의 정보가 담긴 딕셔너리

        Returns:
            {
                "result": {
                    "product": [
                        {
                            "discount_price": 할인가,
                            "discount_rate": 할인율,
                            "id": 상품번호,
                            "image_url": 이미지 URL,
                            "is_displayed": 진열여부,
                            "is_selling": 판매여부,
                            "korean_brand_name": 셀러명,
                            "price": 상품가격,
                            "product_code": 상품코드,
                            "seller_id": 셀러아이디,
                            "sub_property": 셀러구분,
                            "title": 상품명,
                            "upload_date": 등록일자
                        }
                    ],
                    "total_count": 총 상품 수
                },
                "status_code": 200
            }
            500: Exception
        """
        conn = None
        try:
            params = valid.get_params()
            params['account_id'] = g.account_id
            params['account_type_id'] = g.account_type_id
            headers = valid.get_headers()
            conn = get_connection()
            
            result = self.service.get_products_list(conn, params, headers)
            
            # HEADERS로 엑셀파일 요청
            if 'application/vnd.ms-excel' in headers.values():
                today = datetime.today().strftime('%Y-%m-%d')
                return send_file(result, attachment_filename=f'{today}product_list.xls', as_attachment=True)

            return get_response(result)

        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    raise DatabaseCloseFail('알 수 없는 오류가 발생했습니다.')
    
    # 상품 등록
    @LoginRequired('seller')
    def post(self):
        """상품 등록

        상품 등록 페이지에서 들어오는 정보를 받고 DB에 입력한다.

        Raises:
            RequiredDataError: 필수 데이터가 없을 시 발생하는 에러
            DatabaseCloseFail: 데이터베이스와 연결을 끊을 때 발생하는 에러
            e: 등록되지 않은 에러 발생한 경우

        Returns:
            200, message: 성공시 성공 메세지 반환
        """
        conn = None
        try:
            imgs_obj = request.files.getlist('file')
            payload = request.form.get('payload')
            body = json.loads(payload)

            if not imgs_obj:
                raise RequiredDataError('상품 이미지를 입력하세요.') 

            if 'basic_info' not in body:
                raise RequiredDataError('상품 기본 정보를 입력하세요.')

            if 'selling_info' not in body:
                raise RequiredDataError('상품 판매 정보를 입력하세요.')
            
            basic_info = body['basic_info']
            selling_info = body['selling_info']
            option_info = body.get('option_info', None)

            # 필수 입력값 확인
            if 'seller_id' not in basic_info:
                raise RequiredDataError('판매자 정보를 입력하세요.')

            if 'is_selling' not in basic_info:
                raise RequiredDataError('판매여부를 선택하세요.')

            if 'is_displayed' not in basic_info:
                raise RequiredDataError('진열여부를 선택하세요.')

            if 'property_id' not in basic_info:
                raise RequiredDataError('판매자 속성을 선택하세요.')

            if 'category_id' not in basic_info:
                raise RequiredDataError('1차 카테고리를 선택하세요.')

            if 'sub_category_id' not in basic_info:
                raise RequiredDataError('2차 카테고리를 선택하세요.')

            if 'title' not in basic_info:
                raise RequiredDataError('상품명을 입력하세요.')

            if 'content' not in basic_info:
                raise RequiredDataError('상품 상세 정보를 입력하세요.')

            if 'price' not in selling_info:
                raise RequiredDataError('상품 가격을 입력하세요.')

            conn = get_connection()

            # products 테이블에 정보 입력
            product_id = self.service.create_product_info(conn, basic_info, selling_info)

            # 옵션이 존재하면 options 테이블에 정보 입력
            if option_info:

                for option in option_info:

                    if 'price' not in option:
                        raise RequiredDataError('옵션 상품 가격을 입력하세요.')

                self.service.create_option_info(conn, product_id, option_info)
            
            # s3에 상품 이미지 파일 업로드
            self.service.insert_image_url(conn, product_id, imgs_obj)
            
            conn.commit()

            return post_response_success('상품 등록이 완료되었습니다.')

        except Exception as e:
            if conn:
                conn.rollback()
            raise e

        except ValueError:
            if conn:
                conn.rollback()
            raise DataCannotBeConverted('입력값의 총 형식이 잘못되어 읽어들일 수 없습니다.')

        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    raise DatabaseCloseFail('알 수 없는 오류가 발생했습니다.')
    
    # 상품 리스트에서 상품의 판매여부, 진열여부 수정
    @LoginRequired('seller')
    def patch(self):
        """상품 판매, 진열여부 수정

        요청으로 들어온 상품번호의 상품 판매여부, 진열여부를 수정한다.

        Returns:
            "SUCCESS" (dict) : 성공했을 때, Success 메시지를 반환 
            product_check_fail_result (dict) : 일부 값 변경에 실패할 경우 실패한 값을 반환
        """
        conn = None
        try:
            params = request.get_json()
            conn = get_connection()
            product_check_fail_result = self.service.patch_product_selling_or_display_status(conn, params)
            
            conn.commit()
            
            # 상태변경에 실패한 경우
            if product_check_fail_result:
                return post_response_with_return('상품이 존재하지 않거나 권한이 없습니다.', product_check_fail_result, 400)
            
            return post_response('SUCCESS')

        finally:
            try:
                conn.close()
            except Exception as e:
                raise DatabaseCloseFail('알 수 없는 오류가 발생했습니다.')

class ProductDetailView(MethodView):
    def __init__(self, service):
        self.service = service

    # 상품 상세 가져오기
    @LoginRequired('seller')
    @validate_params(
        Param('product_code', PATH, str)
    )
    def get(self, valid: ValidRequest, product_code):
        """상품 상세 조회
        
        해당 상품코드를 가진 상품 상세 정보 출력

        Args:
            valid (ValidRequest): validate_params 데코레이터로 전달된 값
            product_code (str): PATH params 로 들어온 상품코드

        Raises:
            DatabaseCloseFail: 데이터베이스 close 에러

        Returns:
            [dict]: 상품의 정보, 옵션, 이미지 정보
        """
        conn = None
        try:
            conn = get_connection()
            params = valid.get_path_params()
            result = self.service.get_product_detail(conn, params)
            
            return get_response(result)
        
        finally:
            try:
                conn.close()
            except Exception as e:
                raise DatabaseCloseFail('알 수 없는 오류가 발생했습니다.')
    
    # 상품 등록 페이지에서 수정
    @LoginRequired('seller')
    def patch(self, product_code: str):
        conn = None
        try:
            imgs_obj = request.files.getlist('file')
            payload = request.form.get('payload')
            body = literal_eval(payload)
            
            if not imgs_obj:
                raise RequiredDataError('상품 이미지를 입력하세요.') 

            if 'basic_info' not in body:
                raise RequiredDataError('상품 기본 정보를 입력하세요.')

            if 'selling_info' not in body:
                raise RequiredDataError('상품 판매 정보를 입력하세요.')
            
            basic_info = body['basic_info']
            selling_info = body['selling_info']
            option_info = body.get('option_info', None)

            # 필수 입력값 확인
            if 'product_id' not in basic_info:
                raise RequiredDataError('상품 정보가 없습니다.')

            if 'seller_id' not in basic_info:
                raise RequiredDataError('판매자 정보를 입력하세요.')

            if 'is_selling' not in basic_info:
                raise RequiredDataError('판매여부를 선택하세요.')

            if 'is_displayed' not in basic_info:
                raise RequiredDataError('진열여부를 선택하세요.')

            if 'property_id' not in basic_info:
                raise RequiredDataError('판매자 속성을 선택하세요.')

            if 'category_id' not in basic_info:
                raise RequiredDataError('1차 카테고리를 선택하세요.')

            if 'sub_category_id' not in basic_info:
                raise RequiredDataError('2차 카테고리를 선택하세요.')

            if 'title' not in basic_info:
                raise RequiredDataError('상품명을 입력하세요.')

            if 'content' not in basic_info:
                raise RequiredDataError('상품 상세 정보를 입력하세요.')

            if 'price' not in selling_info:
                raise RequiredDataError('상품 가격을 입력하세요.')

            product_id = basic_info['product_id']

            conn = get_connection()
            
            self.service.patch_products_info(conn, basic_info, selling_info)

            if option_info:

                for option in option_info:

                    if 'price' not in option:
                        raise RequiredDataError('옵션 상품 가격을 입력하세요.')
                
                self.service.patch_option_info(conn, product_id, option_info)
            
            # s3에 이미지 업로드
            self.service.update_image_url(conn, product_id, imgs_obj)

            conn.commit()
            
            return post_response_success('상품 수정을 완료하였습니다.')
        
        finally:
            try:
                conn.close()
            except Exception:
                raise DatabaseCloseFail('알 수 없는 오류가 발생했습니다.')


class ProductSellerSearchView(MethodView):
    def __init__(self, service):
        self.service = service

    # 상품 등록 -> 셀러 검색
    @LoginRequired('master')
    @validate_params(
        Param('search', GET, str, required=False)
    )
    def get(self, valid: ValidRequest):
        conn = None
        try:
            params = valid.get_params()
            keyword = params.get('search', None)
            conn = get_connection()

            if keyword:
                result = self.service.search_seller(conn, keyword)
            else:
                result = []
            
            return get_response(result)
        
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    raise DatabaseCloseFail('알 수 없는 오류가 발생했습니다.')


class ProductSellerView(MethodView):
    def __init__(self, service):
        self.service = service

    # seller 속성, 1차 카테고리
    @LoginRequired('master')
    def get(self, seller_id: int):
        conn = None
        try:
            conn = get_connection()
            result = self.service.get_property_and_available_categories_list(conn, seller_id)
            return get_response(result)

        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    raise DatabaseCloseFail('알 수 없는 오류가 발생했습니다.')


class ProductSubCategoryView(MethodView):
    def __init__(self, service):
        self.service = service

    # 상품 등록 -> 2차 카테고리 선택
    def get(self, category_id: int):
        conn = None
        try:
            conn = get_connection()
            result = self.service.get_sub_categories_list(conn, category_id)
            return get_response(result)

        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    raise DatabaseCloseFail('알 수 없는 오류가 발생했습니다.')


class ProductColorView(MethodView):
    def __init__(self, service):
        self.service = service

    def get(self):
        conn = None
        try:
            conn = get_connection()
            result = self.service.get_products_color_list(conn)
            return get_response(result)

        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    raise DatabaseCloseFail('알 수 없는 오류가 발생했습니다.')


class ProductSizeView(MethodView):
    def __init__(self, service):
        self.service = service

    def get(self):
        conn = None
        try:
            conn = get_connection()
            result= self.service.get_products_size_list(conn)
            return get_response(result)
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    raise DatabaseCloseFail('알 수 없는 오류가 발생했습니다.')


class ProductContentImageView(MethodView):
    def __init__(self, service):
        self.service = service
    
    @LoginRequired('seller')
    def post(self):
        img_obj = request.files.get('file')
        url = self.service.create_product_html_image_url(img_obj)
        if not url:
            raise UploadFailtoS3('이미지 업로드에 실패하였습니다.')
        return post_response(url)