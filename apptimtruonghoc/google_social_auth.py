# # apptimtruonghoc/google_social_auth.py
# from google.auth.transport import requests
# from google.oauth2 import id_token
# import logging

# logger = logging.getLogger(__name__)

# class Google:
#     @staticmethod
#     def validate(auth_token):
#         try:
#             idinfo = id_token.verify_oauth2_token(
#                 auth_token,
#                 requests.Request())


#             # In ra để xem kết quả
#             logger.info(f"ID Token verification successful. User data: {idinfo}")

#             if 'accounts.google.com' in idinfo['iss']:
#                 return idinfo

#         except Exception as e:
#             # In ra lỗi cụ thể
#             logger.error(f"Error validating Google ID Token: {e}")
#             return "The token is either invalid or has expired"


# File: google.py (ví dụ)
from google.oauth2 import id_token
from google.auth.transport import requests


GOOGLE_CLIENT_ID='875195545395-kh54279ju4pea3h5n1b85uj3hohn0aih.apps.googleusercontent.com'

class Google:
    @staticmethod
    def validate(auth_token):
        try:
            # Hàm này sẽ tự động xác minh và giải mã token.
            # Nếu token hết hạn hoặc không hợp lệ, nó sẽ ném ra ValueError.
            idinfo = id_token.verify_oauth2_token(
                auth_token,
                requests.Request(),
                GOOGLE_CLIENT_ID
            )
            # Nếu thành công, idinfo sẽ là một dictionary.
            return idinfo
        except ValueError as e:
            # Xử lý trường hợp token không hợp lệ hoặc hết hạn.
            # Rất quan trọng: Phải ném ra một ngoại lệ ở đây.
            # KHÔNG trả về một chuỗi!
            raise ValueError(f"Token validation failed: {e}")