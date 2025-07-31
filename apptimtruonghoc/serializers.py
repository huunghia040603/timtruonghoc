from rest_framework import serializers
from .models import * # Đảm bảo bạn đã import tất cả các models cần thiết
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.socialaccount.models import SocialAccount


# ---
## Serializers Người Dùng (User)
# ---
# class UserSerializer(serializers.ModelSerializer):
#     age = serializers.IntegerField(read_only=True) # age là một @property, chỉ đọc

#     class Meta:
#         model = User
#         fields = [
#             'id', 'email', 'first_name', 'last_name', 'date_of_birth',
#             'living_place', 'role', 'user_level', 'is_active_user', 'age',
#             'username', 'user_photo' # Thêm user_photo
#         ]
#         # Thêm 'password' vào extra_kwargs để đảm bảo nó được ghi nhưng không đọc ra ngoài
#         extra_kwargs = {
#             'password': {'write_only': True, 'required': False} # password không bắt buộc khi update
#         }

#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         return user

#     def update(self, instance, validated_data):
#         # Xử lý trường password riêng nếu có
#         password = validated_data.pop('password', None)
#         user = super().update(instance, validated_data)
#         if password:
#             user.set_password(password)
#             user.save()
#         return user



class UserSerializer(UserDetailsSerializer): # Đây là serializer cho /api/v1/auth/user/ và UserViewSet
    age = serializers.IntegerField(read_only=True)

    class Meta(UserDetailsSerializer.Meta):
        model = User
        fields = (
            'pk', 'email', 'first_name', 'last_name', 'date_of_birth',
            'living_place', 'role', 'user_level', 'is_active_user', 'user_photo',
            'is_superuser', 'is_staff', 'age', 'password' # Thêm password để cho phép tạo/cập nhật admin
        )
        read_only_fields = ('pk', 'is_superuser', 'is_staff', 'age') # email có thể chỉnh sửa, role có thể chỉnh sửa bởi admin
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    # Override create để xử lý mật khẩu
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    # Override update để xử lý mật khẩu
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    # Bạn có thể thêm method để lấy social accounts nếu muốn
    # social_accounts = serializers.SerializerMethodField()

    # def get_social_accounts(self, obj):
    #     accounts = SocialAccount.objects.filter(user=obj)
    #     return [{'provider': a.provider, 'uid': a.uid} for a in accounts]



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






class CustomLoginSerializer(LoginSerializer):
    username = None # Vô hiệu hóa trường username
    email = serializers.EmailField(required=True, allow_blank=False)

class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    def custom_signup(self, request, user):
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        # Bạn có thể thêm các trường khác nếu cần
        user.save()

