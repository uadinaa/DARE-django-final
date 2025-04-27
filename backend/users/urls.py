from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    ProfileViewSet,
    UserProfileUpdateView,
    UserViewSet,
    AdminUserBlockView,
    AdminUserUnblockView
)

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('', include(router.urls)),
    # Admin actions
    path('<int:pk>/block/', AdminUserBlockView.as_view(), name='admin-user-block'),
    path('<int:pk>/unblock/', AdminUserUnblockView.as_view(), name='admin-user-unblock'),
]