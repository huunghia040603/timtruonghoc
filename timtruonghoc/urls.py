



# timtruonghoc/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apptimtruonghoc import views # Import views từ app của bạn


schema_view = get_schema_view(
    openapi.Info(
        title="TimTruongHoc API",
        default_version='v1',
        description="APIs for TimTruongHoc",
        contact=openapi.Contact(email="timtruonghocvn@gmail.com"),
        license=openapi.License(name="TimTruongHoc@2025"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apptimtruonghoc.urls')),
    # Các URL của dj-rest-auth và allauth cho API authentication
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),

    # Các URL cụ thể cho social login API
    path('api/v1/auth/google/connect/', include('allauth.socialaccount.providers.google.urls')),
    path('api/v1/auth/facebook/connect/', include('allauth.socialaccount.providers.facebook.urls')),
    path('api/v1/auth/google/login/', views.GoogleLogin.as_view(), name='google_login_api'),
    path('api/v1/auth/facebook/login/', views.FacebookLogin.as_view(), name='facebook_login_api'),

    # URLs cho JWT
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Các API tài nguyên của ứng dụng apptimtruonghoc (tất cả sẽ nằm dưới /api/v1/)
    path('api/v1/', include('apptimtruonghoc.urls')),

    # CKEditor URLs
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # Các trang HTML hoặc các URL không phải API
    # Giữ các đường dẫn này nếu bạn muốn các trang HTML truy cập trực tiếp
    path('account/', views.account_view, name='account'), # Trang tài khoản HTML
    path('account/success/', views.account_success_view, name='account_success'), # Trang thành công HTML

    # URLs cho DRF-YASG
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    re_path(r'^swagger/$',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
    re_path(r'^redoc/$',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),
]









# from django.contrib import admin
# from django.urls import path, include, re_path
# from drf_yasg import openapi
# from drf_yasg.views import get_schema_view
# from rest_framework import permissions
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

# from apptimtruonghoc import views

# schema_view = get_schema_view(
#     openapi.Info(
#         title="TimTruongHoc API",
#         default_version='v1',
#         description="APIs for TimTruongHoc",
#         contact=openapi.Contact(email="timtruonghocvn@gmail.com"),
#         license=openapi.License(name="TimTruongHoc@2025"),
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

# urlpatterns = [

#     path('admin/', admin.site.urls),

#     path('api/v1/auth/', include('dj_rest_auth.urls')), # Login, logout, user details, password reset
#     path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')), # Register


#     path('api/v1/auth/google/connect/', include('allauth.socialaccount.providers.google.urls'), name='google_connect'),
#     path('api/v1/auth/facebook/connect/', include('allauth.socialaccount.providers.facebook.urls'), name='facebook_connect'),
#     # Với luồng đăng nhập social qua API:
#     path('api/v1/auth/google/login/', views.GoogleLogin.as_view(), name='google_login'),
#     path('api/v1/auth/facebook/login/', views.FacebookLogin.as_view(), name='facebook_login'),


#     # URLs cho JWT (nếu bạn dùng JWT)
#     path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

#     # URLs cho các API khác của bạn
#     path('api/v1/', include('apptimtruonghoc.urls')), # Ví dụ: app của bạn có file urls.py riêng
#     path('ckeditor/', include('ckeditor_uploader.urls')),

#     re_path(r'^swagger(?P<format>\.json|\.yaml)$',
#             schema_view.without_ui(cache_timeout=0),
#             name='schema-json'),
#     re_path(r'^swagger/$',
#             schema_view.with_ui('swagger', cache_timeout=0),
#             name='schema-swagger-ui'),
#     re_path(r'^redoc/$',
#             schema_view.with_ui('redoc', cache_timeout=0),
#             name='schema-redoc'),
# ]

