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
    RequestTrainerVerificationView,
    AdminVerifyTrainerView,
    ProcessTrainerVerificationView,
    TrainerStatsView,
)

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", CurrentUserDetailView.as_view(), name="current-user-detail"),
    path("me/profile/", UserProfileUpdateView.as_view(), name="current-user-profile-update"),
    path("me/stats/", TrainerStatsView.as_view(), name="trainer-stats"),
    path("", include(router.urls)),
    path('trainers/top/', TopTrainersListView.as_view(), name='top-trainers-list'),
    path('trainers/all/', AllTrainersListView.as_view(), name='all-trainers-list'),
    # Admin actions
    path("<int:pk>/block/", AdminUserBlockView.as_view(), name="admin-user-block"),
    path("<int:pk>/unblock/", AdminUserUnblockView.as_view(), name="admin-user-unblock"),
    path("me/request-trainer-verification/", RequestTrainerVerificationView.as_view(), name="request-trainer-verification"), # URL для админских действий (пример)
    path("admin/verify-trainer/<int:user_id>/<str:verification_action>/", AdminVerifyTrainerView.as_view(), name="admin-verify-trainer"), # verification_action может быть 'approve' или 'reject'
    path("verify-trainer-action/<str:user_id_b64>/<uuid:token>/<str:action>/", ProcessTrainerVerificationView.as_view(), name="admin-process-verification"),
]
