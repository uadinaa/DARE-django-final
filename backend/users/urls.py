from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminUserBlockView,
    AdminUserUnblockView,
    RegisterView,
    UserProfileUpdateView,
    UserViewSet,
    TopTrainersListView
)

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", UserProfileUpdateView.as_view(), name="user-profile-update"),
    path("", include(router.urls)),
    path('trainers/top/', TopTrainersListView.as_view(), name='top-trainers-list'),
    # Admin actions
    path("<int:pk>/block/", AdminUserBlockView.as_view(), name="admin-user-block"),
    path(
        "<int:pk>/unblock/", AdminUserUnblockView.as_view(), name="admin-user-unblock"
    ),
]
