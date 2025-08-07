from rest_framework import serializers
from .models import *
import os
from .utils import register_social_user
from .google_social_auth import Google
import logging
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

logger = logging.getLogger(__name__)

GOOGLE_CLIENT_ID='875195545395-kh54279ju4pea3h5n1b85uj3hohn0aih.apps.googleusercontent.com'



class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = None # Khởi tạo biến để tránh lỗi

        try:
            # 1. Xác minh token với Google
            # Hàm này sẽ ném ra lỗi nếu token không hợp lệ/hết hạn.
            user_data = Google.validate(auth_token)

            # In ra log để debug (có thể bỏ đi sau)
            print(f"User data from Google: {user_data}")

            # 2. Kiểm tra Client ID
            # Dòng này chỉ được thực thi nếu Google.validate() thành công và trả về dictionary.
            if user_data.get('aud') != GOOGLE_CLIENT_ID:
                logger.error(f"Client ID mismatch. Received aud: {user_data.get('aud')}, Expected: {GOOGLE_CLIENT_ID}")
                raise serializers.ValidationError(
                    'Oops, who are you? Please re-login.'
                )

        except Exception as e:
            # Bắt các lỗi từ Google.validate() và các lỗi khác.
            logger.error(f"Error validating Google ID token: {e}")
            raise serializers.ValidationError(
                f'The token is invalid or expired. Please login again. Detail: {e}'
            )

        # 3. Gọi hàm đăng ký/đăng nhập người dùng social
        # ...
        try:
            return register_social_user(
                provider='google',
                user_id=user_data['sub'],
                email=user_data['email'],
                name=user_data['name'],
                user_photo=user_data.get('picture')
            )
        except Exception as e:
            logger.error(f"An error occurred during social user registration: {e}")
            raise serializers.ValidationError(
                f'An error occurred. Please try again. Error: {e}'
            )



# ---
## Serializers Người Dùng (User)
# ---
class UserSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)  # age là một @property, chỉ đọc

    # Tạo một trường password riêng để handle việc cập nhật mật khẩu
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'date_of_birth',
            'living_place', 'role', 'user_level', 'is_active_user', 'age','sex',
             'user_photo', 'password' # Thêm password vào fields
        ]

        # Đặt first_name và last_name là read_only
        read_only_fields = ['email']

        # Xóa extra_kwargs cho password vì chúng ta đã tạo trường password riêng
        # và handle logic trong update() method.

    def create(self, validated_data):
        # Tách password ra để tạo user
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        # Xử lý trường password riêng nếu có trong validated_data
        password = validated_data.pop('password', None)

        # Cập nhật các trường còn lại
        user = super().update(instance, validated_data)

        # Đặt lại mật khẩu nếu password được cung cấp
        if password:
            user.set_password(password)
            user.save()

        return user



# ---
## Serializers Nhóm Lĩnh Vực (FieldGroup)
# ---
class FieldGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldGroup
        fields = [
            'field_id',
            'name',
            'description',
            'cover' # Thêm trường 'cover' vào đây để nó được hiển thị
        ]

# ---
## Serializers Album
# ---
class AlbumSerializer(serializers.ModelSerializer):
    images = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Album
        fields = '__all__'

# ---
## Serializers Image
# ---
class ImageSerializer(serializers.ModelSerializer):
    album_name = serializers.CharField(source='album.name', read_only=True)

    class Meta:
        model = Image
        fields = '__all__'

# ---
## Serializers cho AdmissionScore (Điểm chuẩn)
# ---
# Serializer chi tiết cho AdmissionScore khi lồng trong Major
class AdmissionScoreDetailSerializer(serializers.ModelSerializer):
    """
    Serialzer này được sử dụng khi lồng các điểm chuẩn vào MajorSerializer.
    """
    class Meta:
        model = AdmissionScore
        # Trong model AdmissionScore, trường điểm chuẩn là 'score'
        fields = ['year', 'score']

# Serializer độc lập cho AdmissionScore (khi không lồng)
class AdmissionScoreStandaloneSerializer(serializers.ModelSerializer):
    """
    Serializer này được sử dụng khi truy vấn AdmissionScore một cách độc lập.
    Nó sẽ hiển thị tên ngành liên quan.
    """
    # major_name là tên hiển thị của ngành, lấy từ major.name
    major_name = serializers.CharField(source='major.name', read_only=True)

    class Meta:
        model = AdmissionScore
        # Bao gồm major (khóa ngoại) để có thể tạo/cập nhật điểm chuẩn cho một ngành cụ thể
        fields = ['id', 'major', 'major_name', 'year', 'score']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=AdmissionScore.objects.all(),
                fields=['major', 'year'],
                message="Điểm chuẩn cho ngành này và năm này đã tồn tại."
            )
        ]

# ---
## Serializers Ngành riêng của từng trường (Major) - Phiên bản ĐƠN GIẢN
# ---
class MajorSimpleSerializer(serializers.ModelSerializer):
    """
    Serialzer đơn giản cho Major, chỉ bao gồm các thông tin cơ bản.
    Được sử dụng khi lồng trong SchoolSimpleSerializer để tránh vòng lặp đệ quy.
    """
    class Meta:
        model = Major
        fields = ['id', 'major_id', 'name'] # Chỉ các trường cơ bản

# ---
## Serializers Trường học (School) - Phiên bản ĐƠN GIẢN
# ---
class SchoolSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer đơn giản cho School, chỉ bao gồm các trường cơ bản và danh sách ngành.
    Được sử dụng khi lồng trong MajorSerializer để tránh vòng lặp đệ quy.
    """
    # Sử dụng MajorSimpleSerializer để lồng danh sách ngành, related_name là 'school_major'
    majors_data = MajorSimpleSerializer(source='school_major', many=True, read_only=True)

    class Meta:
        model = School
        fields = [
            'id', 'name_vn', 'name_en', 'logo', 'short_code', 'admission_code',
            'school_type', 'website_url', 'phone_number', 'email', 'country',
            'school_level', 'tag', 'majors_data','socialmedialink'
        ]

# ---
## Serializers Ngành riêng của từng trường (Major) - Phiên bản ĐẦY ĐỦ
# ---
class MajorSerializer(serializers.ModelSerializer):
    # Sử dụng SchoolSimpleSerializer để hiển thị thông tin trường
    # Điều này tránh được lỗi vòng lặp đệ quy giữa MajorSerializer và SchoolSerializer đầy đủ
    school = SchoolSimpleSerializer(read_only=True)
    school_id = serializers.PrimaryKeyRelatedField(queryset=School.objects.all(), source='school', write_only=True, required=True)

    # Lấy điểm chuẩn liên quan đến Major này
    admission_scores = AdmissionScoreDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Major
        fields = '__all__' # Bao gồm tất cả các trường và trường lồng ghép

# ---
## Serializers Ngành Chung của tất cả trường học (AllMajorOfAllSchool)
# ---
class AllMajorOfAllSchoolSerializer(serializers.ModelSerializer):
    # Sử dụng FieldGroupSerializer đã tạo để hiển thị chi tiết FieldGroup
    # read_only=True sẽ hiển thị dữ liệu của FieldGroup, bao gồm cả 'cover'
    field = FieldGroupSerializer(read_only=True)

    # field_id vẫn dùng cho việc ghi dữ liệu (tạo/sửa)
    field_id = serializers.PrimaryKeyRelatedField(
        queryset=FieldGroup.objects.all(),
        source='field',
        write_only=True,
        required=True
    )

    class Meta:
        model = AllMajorOfAllSchool
        # Liệt kê tất cả các fields mà bạn muốn hiển thị
        fields = [
            'id','all_major_id','name','short_description','training_duration','job','suitable',
            'program','salary','cover','tuition_fee_per_year','field',
            'field_id', 'note','opportunities','tag'
        ]

# ---
## Serializers Bảng con phân quyền (Admin, Staff, Partner)
# ---
class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True, required=True
    )

    class Meta:
        model = Admin
        fields = ['user', 'user_id', 'create']
        read_only_fields = ['create']

class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True, required=True
    )

    class Meta:
        model = Staff
        fields = ['user', 'user_id', 'create']
        read_only_fields = ['create']

class PartnerSerializer(serializers.ModelSerializer):
    # Sử dụng SchoolSimpleSerializer để hiển thị thông tin trường liên quan
    school = SchoolSimpleSerializer(read_only=True)
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(), source='school', write_only=True, required=True
    )

    class Meta:
        model = Partner
        fields = [
            'school', 'school_id', 'contact_person', 'contract_start_date',
            'contract_end_date', 'contract_details', 'is_active_partner'
        ]

# ---
## Serializers Trường học (School) - GIỮ NGUYÊN NHƯ YÊU CẦU (Phiên bản ĐẦY ĐỦ)
# ---
class SchoolSerializer(serializers.ModelSerializer):
    # Sử dụng MajorSerializer đầy đủ để hiển thị chi tiết ngành
    majors_data = MajorSerializer(source='school_major', many=True, read_only=True)
    album_details = AlbumSerializer(source='album', read_only=True)

    album_id = serializers.PrimaryKeyRelatedField(
        queryset=Album.objects.all(),
        source='album',
        allow_null=True,
        required=False
    )

    class Meta:
        model = School
        fields = [
            'id', 'name_en', 'name_vn', 'short_code', 'admission_code', 'logo','cover_photo', 'established_year', 'school_type',
            'website_url', 'quota_per_year','introduction', 'phone_number', 'email', 'map_link', 'start', 'end',
            'album_id','scholarships', 'school_level','majors_data','country','registration',
            'album_details', 'benchmark_min', 'benchmark_max', 'tag', 'address','socialmedialink'
        ]
        read_only_fields = [
            'majors_data', 'album_details'
        ]




class SchoolOutstandingSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['name_vn', 'logo','short_code']





