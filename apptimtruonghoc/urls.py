from django.urls import path, include
from rest_framework import routers
from .views import *
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)

# Create a default router
r = routers.DefaultRouter()

# Register each ViewSet with the router
r.register('users', UserViewSet, basename='users')
r.register('fieldgroups', FieldGroupViewSet, basename='fieldgroups')
r.register('majors-outstanding', OutstandingMajorViewSet, basename='majors-outstanding')
r.register('majors', AllMajorViewSet, basename='majors')
r.register('albums', AlbumViewSet, basename='albums')
r.register('images', ImageViewSet, basename='images')
r.register('schools', SchoolViewSet, basename='schools')
r.register('schools_outstanding', OutstandingSchoolViewSet, basename='schools_outstanding')
r.register('admission-scores', AdmissionScoreViewSet, basename='admission-scores')
r.register('admins', AdminViewSet, basename='admins')
r.register('staffs', StaffViewSet, basename='staffs')
r.register('partners', PartnerViewSet, basename='partners')
r.register('all_major', AllMajorViewByField, basename='all_major')
r.register('all_major_has_pagi', AllMajorViewByFieldHasPagi, basename='all_major_has_pagi')


urlpatterns = [
    # Include the router-generated URLs
    path('', include(r.urls)),

    # Thêm URL cho GoogleSocialAuthView
    path('auth/google-social-auth/', GoogleSocialAuthView.as_view(), name='google-social-auth'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]




# from django.contrib import admin
# from django.urls import path, include
# from rest_framework import routers
# from .views import *

# # Create a default router
# r = routers.DefaultRouter()

# # Register each ViewSet with the router
# r.register('users', UserViewSet, basename='users')
# r.register('fieldgroups', FieldGroupViewSet, basename='fieldgroups')
# r.register('majors-outstanding', OutstandingMajorViewSet, basename='majors-outstanding')
# r.register('majors', AllMajorViewSet, basename='majors')
# r.register('albums', AlbumViewSet, basename='albums')
# r.register('images', ImageViewSet, basename='images')
# r.register('schools', SchoolViewSet, basename='schools')
# r.register('schools_outstanding', OutstandingSchoolViewSet, basename='schools_outstanding')
# r.register('admission-scores', AdmissionScoreViewSet, basename='admission-scores')
# r.register('admins', AdminViewSet, basename='admins')
# r.register('staffs', StaffViewSet, basename='staffs')
# r.register('partners', PartnerViewSet, basename='partners')
# r.register('all_major', AllMajorViewByField, basename='all_major')
# r.register('all_major_has_pagi', AllMajorViewByFieldHasPagi, basename='all_major_has_pagi')


# # Configure urlpatterns for your application
# urlpatterns = [
#     # Include the router-generated URLs
#     path('', include(r.urls)),
#     path('account/', views.account_view, name='account'),
#     path('account/success/', views.account_success_view, name='account_success'),
#     path('auth/google/login/', views.GoogleLogin.as_view(), name='google_login'),
#     path('auth/facebook/login/', views.FacebookLogin.as_view(), name='facebook_login'),

#     # You can add other custom paths here if needed
#     # Example: path('custom-endpoint/', CustomAPIView.as_view()),
# ]
