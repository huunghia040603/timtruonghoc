from django.db.models.signals import pre_save
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login, social_account_added # Đã đổi tên signal
from allauth.socialaccount.models import SocialAccount
from .models import User # Import User model của bạn

@receiver(pre_social_login)
def populate_user_from_social(sender, request, sociallogin, **kwargs):
    # Dùng pre_social_login để xử lý trước khi người dùng được tạo/liên kết
    # Mục đích: kiểm tra email, tạo/cập nhật user model
    user = sociallogin.user
    if user.pk: # Nếu user đã tồn tại (đã từng đăng nhập bằng social này)
        return

    # Nếu đây là lần đầu đăng nhập bằng social account này
    # Cố gắng tìm user dựa trên email nếu email có sẵn
    email = sociallogin.account.extra_data.get('email')
    if email:
        try:
            user_exists = User.objects.get(email=email)
            # Nếu user đã tồn tại với email này, liên kết social account với user đó
            sociallogin.connect(request, user_exists)
            sociallogin.user = user_exists
            return
        except User.DoesNotExist:
            pass # Email chưa tồn tại, sẽ tạo user mới

@receiver(social_account_added)
def update_user_profile_on_social_connect(sender, request, socialaccount, **kwargs):
    # Signal này được gọi khi một social account được thêm vào user (bao gồm cả lần đăng ký đầu tiên)
    user = socialaccount.user
    extra_data = socialaccount.extra_data

    # Cập nhật first_name và last_name
    if not user.first_name and not user.last_name: # Chỉ cập nhật nếu chưa có
        if socialaccount.provider == 'google':
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')
        elif socialaccount.provider == 'facebook':
            # Facebook Graph API thường trả về 'first_name' và 'last_name' trực tiếp
            user.first_name = extra_data.get('first_name', '')
            user.last_name = extra_data.get('last_name', '')
    
    # Cập nhật ảnh đại diện (nếu có)
    if not user.user_photo:
        if socialaccount.provider == 'google':
            user.user_photo = extra_data.get('picture', '')
        elif socialaccount.provider == 'facebook':
            # Để lấy ảnh đại diện từ Facebook, bạn cần yêu cầu thêm scope 'user_photos' hoặc truy cập qua Graph API
            # Ví dụ: 'https://graph.facebook.com/{id}/picture?type=large'
            # allauth có thể không tự động lấy link ảnh lớn.
            # Bạn có thể cần một request API riêng để lấy ảnh chất lượng cao.
            # Đơn giản nhất là sử dụng URL mặc định mà FB cung cấp (nếu có trong extra_data)
            # Hoặc tạo URL bằng id:
            facebook_id = extra_data.get('id')
            if facebook_id:
                 user.user_photo = f"https://graph.facebook.com/{facebook_id}/picture?type=large"


    user.save()

