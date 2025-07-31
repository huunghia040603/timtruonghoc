# apptimtruonghoc/urls.py

from django.urls import path, include
from rest_framework import routers
from .views import (
    UserViewSet, FieldGroupViewSet, OutstandingMajorViewSet, AllMajorViewSet,
    AlbumViewSet, ImageViewSet, SchoolViewSet, OutstandingSchoolViewSet,
    AdmissionScoreViewSet, AdminViewSet, StaffViewSet, PartnerViewSet,
    AllMajorViewByField, AllMajorViewByFieldHasPagi
)

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


# Configure urlpatterns for your application
urlpatterns = [
    # Include the router-generated URLs
    path('', include(r.urls)),
    # XÓA CÁC DÒNG NÀY ĐI VÌ CHÚNG ĐÃ ĐƯỢC DI CHUYỂN VÀO urls.py CHÍNH CỦA PROJECT
    # path('account/', views.account_view, name='account'),
    # path('account/success/', views.account_success_view, name='account_success'),
    # path('auth/google/login/', views.GoogleLogin.as_view(), name='google_login'),
    # path('auth/facebook/login/', views.FacebookLogin.as_view(), name='facebook_login'),

    # You can add other custom paths here if needed for this app's API resources
    # Example: path('custom-api-endpoint/', CustomAPIView.as_view()),
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
