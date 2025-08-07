import re
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .pagination import *
import django_filters
from django.db.models import Case, When, Value, IntegerField, F # Import F for __in lookup
from rest_framework import generics
from .filter import *
from django.shortcuts import render, redirect # THÊM DÒNG NÀY
from django.contrib.auth.decorators import login_required # THÊM DÒNG NÀY
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication



class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Cho phép admin hoặc chính chủ sở hữu được truy cập.
    """
    def has_object_permission(self, request, view, obj):
        # Admin luôn được phép truy cập
        if request.user and (request.user.is_superuser or request.user.is_staff):
            return True

        # Chỉ cho phép chủ sở hữu (người dùng đang đăng nhập) truy cập
        return obj == request.user

class GoogleSocialAuthView(GenericAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = GoogleSocialAuthSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Lấy toàn bộ dictionary đã được validate, chứa token.
        data = serializer.validated_data

        # In ra log để kiểm tra cấu trúc dữ liệu trước khi trả về
        print(f"Data to be returned: {data}")

        return Response(data, status=status.HTTP_200_OK)

# ---
## User ViewSet
# ---
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     def get_permissions(self):
#         # Admin có thể tạo user
#         if self.action == 'create':
#             return [IsAdminUser()]

#         # Cho phép người dùng đã đăng nhập tự sửa/xóa bản thân, và admin có thể sửa/xóa bất kỳ ai
#         elif self.action in ['update', 'partial_update', 'destroy']:
#             return [IsAuthenticated()]

#         # Cho phép xem danh sách (chỉ admin) và xem chi tiết (cho bất kỳ ai)
#         return [AllowAny()]

#     def get_queryset(self):
#         user = self.request.user

#         # Admin có thể xem tất cả user
#         if user and user.is_authenticated and (user.is_superuser or user.is_staff):
#             return User.objects.all()

#         # User thường chỉ xem được thông tin của chính họ
#         if user and user.is_authenticated:
#             return User.objects.filter(id=user.id)

#         return User.objects.none()

#     def perform_update(self, serializer):
#         # Custom logic để chỉ user đang đăng nhập mới có thể update chính họ
#         # hoặc admin update bất kỳ ai
#         instance = self.get_object()
#         user = self.request.user

#         # Nếu người dùng không phải là admin và đang cố gắng cập nhật người khác, raise exception
#         if not user.is_superuser and not user.is_staff and instance.id != user.id:
#             raise PermissionDenied("You do not have permission to update this user.")

#         serializer.save() # Or User.objects.all() if get_permissions allows general access




class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            # Áp dụng quyền IsAuthenticated và IsOwnerOrAdmin
            return [IsAuthenticated(), IsOwnerOrAdmin()]

        # Đối với các action khác, bạn có thể thiết lập quyền khác
        return [AllowAny()]


# ---
## FieldGroup ViewSet
# ---
class FieldGroupViewSet(viewsets.ModelViewSet):
    queryset = FieldGroup.objects.all()
    serializer_class = FieldGroupSerializer
    lookup_field = 'field_id' # Use 'field_id' for lookup
    permission_classes = [AllowAny] # Allow anyone to view field groups

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

# ---
## Major ViewSet (Chỉ lấy các ngành có tags = 'outstanding')
# ---
class OutstandingMajorViewSet(viewsets.ModelViewSet):
    """
    ViewSet cho mô hình Major, chỉ hiển thị các ngành có tags = 'outstanding'.
    Hỗ trợ hiển thị dữ liệu đơn giản và phức tạp, cùng với phân trang, tìm kiếm, lọc và sắp xếp.
    """
    pagination_class = MajorPagination
    permission_classes = [AllowAny]

    # Thiết lập các backend cho lọc, tìm kiếm và sắp xếp
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Sử dụng filterset_class để chỉ định lớp MajorFilter tùy chỉnh
    filterset_class = MajorFilter # Đã bỏ comment và sử dụng MajorFilter

    # Các trường có thể tìm kiếm
    search_fields = [
        'name',          # Tên ngành
        'major_id',      # Mã ngành
    ]

    # Các trường có thể sắp xếp
    ordering_fields = [
        'name',
        'min_tuition_fee_per_year',
        'max_tuition_fee_per_year',
        'status',
        'tags'
    ]

    # Thiết lập quyền truy cập
    def get_permissions(self):
        """
        Chỉ cho phép admin tạo, cập nhật, xóa ngành.
        Tất cả người dùng đều có thể xem.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    def get_serializer_class(self):
        """
        Trả về serializer class dựa trên hành động (action) và tham số truy vấn (query params).
        - Nếu là hành động 'retrieve' (lấy chi tiết theo ID), luôn trả về MajorSerializer đầy đủ.
        - Nếu có tham số 'simple=true' trong yêu cầu GET danh sách, trả về MajorSimpleSerializer.
        - Mặc định (GET danh sách không có 'simple=true'), trả về MajorSerializer đầy đủ.
        """
        if self.action == 'retrieve':
            return MajorSerializer

        if self.request.query_params.get('simple', 'false').lower() == 'true':
            return MajorSimpleSerializer

        return MajorSerializer

    def get_queryset(self):
        """
        Trả về queryset của các đối tượng Major đã được lọc và sắp xếp ngẫu nhiên.
        DjangoFilterBackend sẽ tự động áp dụng các bộ lọc từ request.query_params
        khi filterset_class được đặt.
        """
        queryset = Major.objects.filter(tags__in=['outstanding', 'pro'])
        # Thêm order_by('?') để sắp xếp ngẫu nhiên
        # Lưu ý: Sắp xếp ngẫu nhiên có thể tốn tài nguyên với tập dữ liệu lớn.
        return queryset.order_by('?')



# ---
## All Major ViewSet (Lấy tất cả các ngành, không lọc theo tags)
# ---
class AllMajorViewSet(viewsets.ModelViewSet):
    """
    ViewSet cho mô hình Major, hiển thị TẤT CẢ các ngành học.
    Hỗ trợ hiển thị dữ liệu đơn giản và phức tạp, cùng với phân trang, tìm kiếm, lọc và sắp xếp.
    """
    queryset = Major.objects.all() # Lấy tất cả các ngành
    permission_classes = [AllowAny]
    # Thiết lập lớp phân trang mặc định
    pagination_class = MajorPagination

    # Thiết lập các backend cho lọc, tìm kiếm và sắp xếp
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Sử dụng filterset_class để chỉ định lớp MajorFilter tùy chỉnh
    # filterset_class = MajorFilter # Bỏ comment nếu bạn có MajorFilter và muốn sử dụng nó

    # Các trường có thể tìm kiếm
    search_fields = [
        'name',           # Tên ngành
        'major_id',       # Mã ngành

    ]

    # Các trường có thể sắp xếp
    ordering_fields = [
        'name',
        'min_tuition_fee_per_year',
        'max_tuition_fee_per_year',
        'status',
        'tags'
    ]

    # Thiết lập quyền truy cập (giống như MajorViewSet)
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    # Thiết lập serializer class (giống như MajorViewSet)
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MajorSerializer

        if self.request.query_params.get('simple', 'false').lower() == 'true':
            return MajorSimpleSerializer

        return MajorSerializer

    # get_queryset không cần tùy chỉnh thêm vì đã lấy tất cả ở queryset ban đầu
    # def get_queryset(self):
    #     return super().get_queryset()




# ---
## Album ViewSet
# ---
class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [AllowAny] # Allow viewing albums

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    @action(detail=True, methods=['get'])
    def images(self, request, pk=None):
        """
        Lấy tất cả ảnh thuộc một album cụ thể.
        """
        album = self.get_object()
        images = album.images.all()
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data)

# ---
## Image ViewSet
# ---
class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [AllowAny] # Allow viewing images

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]


# ---
## School ViewSet
# ---
class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SchoolFilter
    search_fields = [
        'name_en',
        'name_vn',
        'short_code',
        'admission_code',
        'address'
    ]
    ordering_fields = [
        'start',
        'end',
        'benchmark_min',
        'benchmark_max',
        'name_vn',
        'established_year',
    ]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    def get_queryset(self):
        # Lấy queryset ban đầu
        queryset = super().get_queryset()

        # Áp dụng logic sắp xếp tùy chỉnh của bạn
        tag_order = [
            'outstanding',
            'urgency',
            'pro',
            'new',
            'none'
        ]

        ordering = Case(
            *[When(tag=tag_value, then=pos) for pos, tag_value in enumerate(tag_order)],
            default=Value(len(tag_order)),
            output_field=IntegerField()
        )
        queryset = queryset.annotate(tag_order_value=ordering).order_by('tag_order_value', 'id')

        # Thêm logic tìm kiếm trên majors_data nếu cần
        # Lấy giá trị tìm kiếm từ request
        search_query = self.request.query_params.get('search', None)

        if search_query:
            queryset = queryset.filter(majors_data__name__icontains=search_query).distinct()


        return queryset

    # Các phương thức khác của bạn (`majors` và `admission_scores`) không bị ảnh hưởng
    @action(detail=True, methods=['get'])
    def majors(self, request, pk=None):
        school = self.get_object()
        majors = school.school_major.all()
        serializer = MajorSerializer(majors, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def admission_scores(self, request, pk=None):
        school = self.get_object()
        majors_of_school = school.school_major.all()
        admission_scores = AdmissionScore.objects.filter(major__in=majors_of_school).order_by('-year')
        serializer = AdmissionScoreStandaloneSerializer(admission_scores, many=True)
        return Response(serializer.data)

# ---
## AdmissionScore ViewSet
# ---
class AdmissionScoreViewSet(viewsets.ModelViewSet):
    queryset = AdmissionScore.objects.all()
    serializer_class = AdmissionScoreStandaloneSerializer
    permission_classes = [AllowAny] # Allow viewing admission scores

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # Filter by 'major' (ForeignKey) and 'year'
    filterset_fields = ['major', 'year']
    ordering_fields = ['year', 'score'] # Order by 'score' not 'admission_score'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

# ---
## Admin ViewSet
# ---
class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [IsAdminUser] # Only admins can manage other admins

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Admin.objects.all()
        # Admins can only see their own profile
        if hasattr(self.request.user, 'admin_profile'):
            return Admin.objects.filter(user=self.request.user)
        return Admin.objects.none()

# ---
## Staff ViewSet
# ---
class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAdminUser] # Only admins can manage staff

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Staff.objects.all()
        # Staff can only see their own profile
        if hasattr(self.request.user, 'staff_profile'):
            return Staff.objects.filter(user=self.request.user)
        return Staff.objects.none()


# ---
## Partner ViewSet
# ---
class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAdminUser] # Chỉ admin mới có thể quản lý đối tác

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active_partner', 'school']
    search_fields = ['school__name_vn', 'contact_person']

    def get_queryset(self):
        # Đây là dòng cực kỳ quan trọng để giải quyết lỗi drf_yasg
        # Nó kiểm tra xem request có phải là từ drf_yasg để tạo tài liệu hay không.
        if getattr(self, 'swagger_fake_view', False):
            # Nếu là drf_yasg, trả về một queryset rỗng để nó có thể tạo schema
            # mà không cần truy cập các thuộc tính của user hoặc database.
            return Partner.objects.none()

        # Dưới đây là logic khi có một request API thực sự đến view này.
        # Tại thời điểm này, do permission_classes=[IsAdminUser] đã được kiểm tra,
        # self.request.user SẼ LÀ một User đã đăng nhập và có quyền admin.
        # Nếu không, request đã bị từ chối trước khi đến đây.
        if self.request.user.is_superuser or self.request.user.role == 'admin':
            return Partner.objects.all() # Admin xem tất cả
        else:
            # Dòng này về lý thuyết sẽ không bao giờ được thực thi nếu IsAdminUser hoạt động đúng,
            # vì chỉ admin mới được phép truy cập view này.
            # Tuy nhiên, nếu có lý do nào đó (ví dụ: permission class bị override hoặc bỏ qua),
            # nó sẽ xử lý trường hợp người dùng không phải superuser/admin nhưng đã đăng nhập.
            return Partner.objects.filter(owner=self.request.user)

# ---
## Partner AllMajorOfAllSchool
# ---
class AllMajorViewByField(viewsets.ModelViewSet, generics.ListAPIView):
    serializer_class = AllMajorOfAllSchoolSerializer
    permission_classes = [AllowAny]
    # Đã bỏ dòng này: pagination_class = AllMajorPagination

    def get_queryset(self):
        """
        Tùy chỉnh queryset để lọc các ngành học theo `field_id`.
        """
        # Bắt field_id từ query parameters của URL, ví dụ: ?field_id=1
        field_id = self.request.query_params.get('field_id')
        all_major_id = self.request.query_params.get('all_major_id')

        queryset = AllMajorOfAllSchool.objects.all()

        if field_id:
            # Lọc queryset dựa trên field_id
            # Lưu ý: 'field__field_id' cần phải phù hợp với tên trường trong mô hình của bạn
            queryset = queryset.filter(field__field_id=field_id)
        if all_major_id:
            # Lọc queryset dựa trên field_id
            # Lưu ý: 'field__field_id' cần phải phù hợp với tên trường trong mô hình của bạn
            queryset = queryset.filter(all_major_id=all_major_id)

        return queryset




# ---
## Partner AllMajorOfAllSchool
# ---
class AllMajorViewByFieldHasPagi(viewsets.ModelViewSet, generics.ListAPIView):
    serializer_class = AllMajorOfAllSchoolSerializer
    pagination_class = AllMajorPagination
    filterset_class = AllMajorFilter
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    ordering_fields = ['name', 'opportunities', 'tag']

    def get_queryset(self):
        queryset = AllMajorOfAllSchool.objects.all()

        ordering_param = self.request.query_params.get('ordering')

        # --- Logic SẮP XẾP HỌC PHÍ TÙY CHỈNH ĐÃ FIX ---
        # Hàm helper mới, trả về một tuple để sắp xếp chính xác
        def get_tuition_sort_key(tuition_str):
            if not tuition_str:
                return (2, 999999999) # Ưu tiên thấp, giá trị cao (xếp cuối)

            # Ưu tiên cao nhất cho các ngành miễn phí
            if 'miễn phí' in tuition_str.lower():
                return (0, 0) # Ưu tiên 0, giá trị 0 (xếp đầu tiên)

            # Với các ngành có số, ưu tiên thấp hơn (1)
            numbers = re.findall(r'\d+', tuition_str)
            if numbers:
                return (1, int(numbers[0])) # Ưu tiên 1, giá trị là số học phí

            return (2, 999999999) # Các trường hợp còn lại xếp cuối cùng

        if ordering_param in ['tuition_fee_per_year', '-tuition_fee_per_year']:
            majors_list = list(queryset)

            reverse_order = ordering_param.startswith('-')

            # Sử dụng hàm helper mới để sắp xếp
            sorted_majors = sorted(majors_list, key=lambda major: get_tuition_sort_key(major.tuition_fee_per_year), reverse=reverse_order)

            pks_ordered = [major.pk for major in sorted_majors]

            preserved_order = Case(*[When(pk=pk, then=Value(i)) for i, pk in enumerate(pks_ordered)])
            queryset = AllMajorOfAllSchool.objects.filter(pk__in=pks_ordered).order_by(preserved_order)

            return queryset

        # --- Logic SẮP XẾP MẶC ĐỊNH (nếu không có sắp xếp tùy chỉnh) ---
        tag_order = ['hot', 'find', 'grown', 'push', 'normal']
        tag_ordering = Case(*[When(tag=tag_name, then=Value(i)) for i, tag_name in enumerate(tag_order)],
                            output_field=IntegerField())

        return queryset.order_by(tag_ordering)



class OutstandingSchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet chỉ để đọc (Read-Only) cho mô hình School,
    chỉ hiển thị các trường có tag = 'outstanding'.
    Xuất ra tên trường và logo.
    """
    queryset = School.objects.filter(tag='outstanding')
    serializer_class = SchoolOutstandingSerializer
    permission_classes = [AllowAny]



