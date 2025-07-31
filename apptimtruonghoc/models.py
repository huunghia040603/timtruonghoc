from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from ckeditor.fields import RichTextField



from django.contrib.auth.models import UserManager as BaseUserManager

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active_user', True) # Đảm bảo superuser active
        extra_fields.setdefault('role', 'admin') # Đặt vai trò là admin
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)



# ---
## Models Người Dùng (User)
# ---
class User(AbstractUser):
    objects = CustomUserManager()
    ROLE_CHOICES = [
        ('admin', 'Quản trị viên'),
        ('staff', 'Nhân viên'),
        ('partner', 'Đối tác'),
        ('regular_user', 'Người dùng thông thường'),
    ]
    USER_LEVEL_CHOICES = [
        ('primary', 'Tiểu học'),
        ('secondary', 'Trung học cơ sở'),
        ('highschool', 'Trung học phổ thông'),
        ('university', 'Đại học'),
        ('postgraduate', 'Sau đại học'),
        ('other', 'Khác'),
    ]

    email = models.EmailField(unique=True, verbose_name="Email (Tên đăng nhập)")
    first_name = models.CharField(max_length=150,blank=True, null=True, verbose_name="Họ")
    last_name = models.CharField(max_length=150,blank=True, null=True, verbose_name="Tên")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Ngày tháng năm sinh")
    living_place = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nơi sống")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='regular_user', verbose_name="Vai trò")
    user_level = models.CharField(max_length=20, choices=USER_LEVEL_CHOICES, blank=True, null=True, verbose_name="Cấp học (Người dùng)")
    is_active_user = models.BooleanField(default=True, verbose_name="Trạng thái tài khoản")
    user_photo=models.CharField(max_length=255, blank=True, null=True, verbose_name="Ảnh đại diện")
    password= models.CharField(max_length=255, verbose_name="Mật khẩu")

    # Thêm related_name để giải quyết xung đột
    groups = models.ManyToManyField('auth.Group',related_name='apptimtruonghoc_user_set', blank=True,help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',verbose_name='groups')
    user_permissions = models.ManyToManyField('auth.Permission',related_name='apptimtruonghoc_user_permissions_set', blank=True,help_text='Specific permissions for this user.',verbose_name='user permissions',)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'date_of_birth']

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"

    def __str__(self):
        return self.email


# ---
## Models Nhóm Lĩnh Vực
# ---
class FieldGroup(models.Model):
    field_id = models.CharField(max_length=255,blank=True, null=True, verbose_name="Mã lĩnh vực")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên lĩnh vực")
    description = RichTextField(blank=True, null=True, verbose_name="Mô tả")
    cover= models.CharField(max_length=1000, blank=True, null=True, verbose_name="Ảnh bìa")

    class Meta:
        verbose_name = "Nhóm lĩnh vực"
        verbose_name_plural = "Các nhóm lĩnh vực"

    def __str__(self):
        return self.name


# ---
## Models Album
# ---
class Album(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên Album")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả Album")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name_plural = "Album ảnh"


    def __str__(self):
        return self.name

# ---
## Models Image
# ---
class Image(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='images', verbose_name="Album")
    image_file = models.CharField(max_length=500, verbose_name="Đường dẫn ảnh")
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="Chú thích")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tải lên")

    class Meta:
        verbose_name = "Ảnh"
        verbose_name_plural = "Các Ảnh" # <-- This is the corrected line

    def __str__(self):
        return f"Ảnh của {self.album.name} - {self.caption or self.image_file.name}"






# ---
## Models School
# ---
class School(models.Model):
    SCHOOL_TYPE_CHOICES = [
        ('public', 'Công lập'),
        ('private', 'Ngoài công lập'),
        ('international', 'Quốc tế'),

    ]
    LEVEL_CHOICES = [
        ('college', 'Cao đẳng'),
        ('university', 'Đại học'),
        ('vocational', 'Trung cấp')
    ]
    TAGS_CHOICES = [
        ('outstanding', 'Nổi bật'),
        ('pro', 'Chuyên nghiệp'),
        ('new', 'Tin mới'),
        ('urgency', 'Tuyến sinh gấp'),
        ('none', 'Bình thường')
    ]

    name_en = models.CharField(max_length=255, verbose_name="Tên trường tiếng Anh")
    name_vn = models.CharField(max_length=255, verbose_name="Tên trường tiếng Việt")
    short_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã trường viết tắt")
    admission_code = models.CharField(max_length=50,blank=True, null=True, verbose_name="Mã trường tuyển sinh")
    logo = models.CharField(max_length=255,blank=True, null=True, verbose_name="Logo")
    cover_photo = models.CharField(max_length=255,blank=True, null=True, verbose_name="Ảnh bìa")
    established_year = models.IntegerField(blank=True, null=True,verbose_name="Năm thành lập")
    school_type = models.CharField(max_length=20, blank=True, null=True, default='public', choices=SCHOOL_TYPE_CHOICES, verbose_name="Loại trường")
    website_url = models.CharField(max_length=500, blank=True, null=True, verbose_name="Đường dẫn website")
    quota_per_year = models.IntegerField(blank=True, null=True, verbose_name="Chỉ tiêu/năm")
    introduction = RichTextField(verbose_name="Giới thiệu trường", blank=True, null=True, )
    phone_number = models.CharField(max_length=100,blank=True, null=True, verbose_name="Số điện thoại hotline")
    email = models.EmailField(unique=True, verbose_name="Email", blank=True, null=True)
    map_link = models.CharField(max_length=1500, blank=True, null=True, verbose_name="Link bản đồ")
    album = models.OneToOneField(Album, on_delete=models.SET_NULL, null=True, blank=True, related_name='school_linked_to_this_album', verbose_name="Album ảnh của trường")
    scholarships = RichTextField(blank=True, null=True, verbose_name="Học bổng")
    start = models.IntegerField(blank=True, null=True,verbose_name="Học phí tối thiểu")
    end = models.IntegerField(blank=True, null=True,verbose_name="Học phí tối đa")
    country = models.CharField(blank=True, null=True, max_length=100, verbose_name="Khu vực")
    address = RichTextField(blank=True, null=True, verbose_name="Địa chỉ các cơ sở của trường")
    registration= models.BooleanField(blank=True, null=True,verbose_name="Đã đăng ký quảng cáo", default=False)
    tag= models.CharField(max_length=500, blank=True, null=True, default='none', choices=TAGS_CHOICES, verbose_name="Danh mục")
    school_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name="Loại trường (cấp học)")
    benchmark_min = models.IntegerField(blank=True, null=True, verbose_name="Điểm chuẩn tối thiểu của trường tại năm gần nhất")
    socialmedialink= RichTextField(blank=True, null=True, verbose_name="Đường dẫn các trang MXH")
    benchmark_max = models.IntegerField(blank=True, null=True, verbose_name="Điểm chuẩn tối đa của trường tại năm gần nhất")

    class Meta:
        verbose_name = "Trường học"
        verbose_name_plural = "Các trường học"

    def __str__(self):
        return self.name_vn



# ---
## Models Ngành riêng của từng trường
# ---
class Major(models.Model):
    STATUS_CHOICES = [
        ('active', 'Đang hoạt động'),
        ('inactive', 'Ngừng hoạt động'),
    ]
    TAG_CHOICES = [
        ('outstanding', 'Nổi bật'),
        ('pro', 'Chuyên nghiệp'),
        ('none', 'Bình thường'),
    ]

    major_id = models.CharField(max_length=100, verbose_name="Mã ngành")
    name = models.CharField(max_length=190, verbose_name="Tên ngành")
    description = RichTextField(blank=True, null=True, verbose_name="Mô tả ngành")
    entry_requirement= RichTextField( blank=True, null=True, verbose_name="Phương thức xét tuyển")
    min_tuition_fee_per_year= models.CharField(max_length=255,blank=True, null=True, verbose_name="Học phí tối thiểu ngành/năm")
    max_tuition_fee_per_year= models.CharField(max_length=255,blank=True, null=True, verbose_name="Học phí tối đa ngành/năm")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Trạng thái")
    tags = models.CharField(max_length=50, choices=TAG_CHOICES, blank=True, null=True, verbose_name="Tags")
    school= models.ForeignKey(School, on_delete=models.CASCADE, related_name='school_major', verbose_name="Thuộc trường")


    class Meta:
        verbose_name = "Ngành riêng của từng trường"
        verbose_name_plural = "Các ngành riêng cho từng trường"
        unique_together = ('name', 'major_id','school')

    def __str__(self):
        return self.name



# ---
## Models Điểm chuẩn theo từng ngành của từng trường
# ---
class AdmissionScore(models.Model):

    SCORE_TYPE = [
        ('THPT', 'Điểm thi THPTQG'),
        ('HB', 'Điểm xét tuyển học bạ'),
        ('DGNL', 'Điểm thi đánh giá năng lực'),
        ('Khác', 'Khác'),

    ]
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='admission_scores', verbose_name="Ngành")
    year = models.IntegerField(verbose_name="Năm tuyển sinh")
    score = models.FloatField(verbose_name="Điểm chuẩn")
    types = models.CharField(max_length=50, choices=SCORE_TYPE, default='THPT',verbose_name="Loại điểm")

    class Meta:
        verbose_name = "Điểm chuẩn theo ngành"
        verbose_name_plural = "Các điểm chuẩn theo ngành" # Corrected
        unique_together = ( 'major', 'year')

    def __str__(self):
        return f" {self.major.name} (self.types) - Năm {self.year}: {self.score}"



# ---
## Models Ngành Chung của tất cả trường học
# ---
class AllMajorOfAllSchool(models.Model):

    TAG_CHOICES = [
        ('hot', 'Ngành hot'),
        ('find', 'Ngành đang thiếu nhân lực'),
        ('grown', 'Ngành có phát triển'),
        ('push', 'Đẩy mạnh'),
        ('normal', 'Bình thường'),
    ]

    all_major_id = models.CharField(max_length=255, verbose_name="Mã ngành")
    name = models.TextField( verbose_name="Tên ngành")
    short_description= RichTextField(blank=True, null=True,verbose_name="Mô tả của ngành chung")
    training_duration = models.CharField(max_length=255,blank=True, null=True, verbose_name="Thời lượng đào tạo")
    job = RichTextField(blank=True, null=True,verbose_name="Việc làm sau khi học")
    suitable = RichTextField(blank=True, null=True, verbose_name="Tố chất phù hợp")
    program = RichTextField(blank=True, null=True, verbose_name="Chương trình học")
    salary = models.CharField(max_length=255,blank=True, null=True, verbose_name="Thu nhập trung bình")
    cover= models.CharField(max_length=1000, blank=True, null=True, verbose_name="Ảnh bìa")

    tuition_fee_per_year = models.CharField(blank=True, null=True, max_length=255, verbose_name="Khoảng học phí ngành/năm")
    field = models.ForeignKey(FieldGroup, on_delete=models.CASCADE, related_name='field_gr', verbose_name="Thuộc lĩnh vực")
    note = RichTextField(verbose_name="Ghi chú",blank=True, null=True)
    opportunities = models. IntegerField(blank=True, null=True,verbose_name="Cơ hội việc làm của ngành")
    tag = models.CharField(max_length=50, choices=TAG_CHOICES, default='normal',verbose_name="Loại ngành")

    class Meta:
        verbose_name = "Ngành"
        verbose_name_plural = "Các ngành"


    def __str__(self):
        return self.name



# ---
## Bảng con phân quyền
# ---
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='admin_profile')
    create = models.DateTimeField(auto_now=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Quản trị viên"
        verbose_name_plural = "Quản trị viên"

    def __str__(self):
        return f"Admin: {self.user.email} - Tài khoản mở :{self.create} "



class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='staff_profile')
    create = models.DateTimeField(auto_now=True, verbose_name="Ngày vào làm")

    class Meta:
        verbose_name = "Nhân viên"
        verbose_name_plural = "Nhân viên"

    def __str__(self):
        return f"Nhân viên: {self.user.email} - Ngày vào làm :{self.create}"



# ---
## Models Đối tác (Trường học)
# ---
class Partner(models.Model):
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='partner_info', verbose_name="Trường đối tác")
    contact_person = models.CharField(max_length=255, null=True, blank=True, verbose_name="Số điện thoại liên hệ đối tác") # Removed related_name
    contract_start_date = models.DateField(blank=True, null=True, verbose_name="Ngày bắt đầu hợp đồng")
    contract_end_date = models.DateField(blank=True, null=True, verbose_name="Ngày kết thúc hợp đồng")
    contract_details = models.CharField(max_length=255,blank=True, null=True, verbose_name="Chi tiết hợp đồng")
    is_active_partner = models.BooleanField(default=True, verbose_name="Đối tác đang hoạt động")

    class Meta:
        verbose_name = "Đối tác (Trường học)"
        verbose_name_plural = "Các đối tác (Trường học)"

    def __str__(self):
        return f"Đối tác: {self.school.name_vn}"




