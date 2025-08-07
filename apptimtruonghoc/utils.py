# apptimtruonghoc/utils.py

from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
import random
import string

def get_tokens_for_user(user):
    """
    Tạo và trả về cặp access và refresh token cho người dùng.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def generate_random_password(length=12):
    """
    Tạo một mật khẩu ngẫu nhiên.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password


def register_social_user(provider, user_id, email, name, user_photo):
    """
    Đăng ký hoặc đăng nhập người dùng thông qua social.
    """
    try:
        user = User.objects.get(email=email)
        # Người dùng đã tồn tại, trả về token của họ
        tokens = get_tokens_for_user(user)
        return {
            'email': user.email,
            'tokens': tokens,
            'role': user.role,
            'id': user.id,
            'date': user.date_of_birth,
            'live': user.living_place,
            'user_photo': user.user_photo,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'sex': user.sex,
        }
    except User.DoesNotExist:
        # Người dùng chưa tồn tại, tạo tài khoản mới
        if len(name.split()) > 1:
            first_name = name.split()[0]
            last_name = ' '.join(name.split()[1:])
        else:
            first_name = name
            last_name = ''

        password = generate_random_password()

        # SỬA LỖI Ở ĐÂY: Thêm trường username
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            # Thêm trường username. Sử dụng email làm username
            username=email,
            role='regular_user'
            # Bạn cũng có thể dùng user_id của Google làm username để đảm bảo duy nhất
            # username=f'{provider}_{user_id}',
        )
        if user_photo:
            user.user_photo = user_photo
            user.is_active = True
            user.save()

        tokens = get_tokens_for_user(user)

        return {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'tokens': tokens,
            'role': user.role
        }