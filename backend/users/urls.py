from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminUserBlockView,
    AdminUserUnblockView,
    RegisterView,
    UserProfileUpdateView,
    UserViewSet,
    TopTrainersListView,
    CurrentUserDetailView,
    AllTrainersListView,
)

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", CurrentUserDetailView.as_view(), name="current-user-detail"),
    path("me/profile/", UserProfileUpdateView.as_view(), name="current-user-profile-update"),
    path("", include(router.urls)),
    path('trainers/top/', TopTrainersListView.as_view(), name='top-trainers-list'),
    path('trainers/all/', AllTrainersListView.as_view(), name='all-trainers-list'),
    # Admin actions
    path("<int:pk>/block/", AdminUserBlockView.as_view(), name="admin-user-block"),
    path(
        "<int:pk>/unblock/", AdminUserUnblockView.as_view(), name="admin-user-unblock"
    ),
]
