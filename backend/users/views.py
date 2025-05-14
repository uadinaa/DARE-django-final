from django.contrib.auth.models import User
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import Http404

from core.permissions import IsAdminUser, IsProfileOwnerOrAdmin

from .models import Profile
from .serializers import ProfileSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    pass


class UserProfileUpdateView(generics.UpdateAPIView): # <-- Базовый класс изменен
    """
    Обновляет (PUT/PATCH) профиль ТЕКУЩЕГО аутентифицированного пользователя.
    Не обрабатывает GET запросы.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [
        IsAuthenticated,
        IsProfileOwnerOrAdmin,
    ]

    def get_object(self): # Метод get_object ОСТАЕТСЯ
        try:
            return self.request.user.profile
        except Profile.DoesNotExist:
            raise Http404("Профиль для этого пользователя не найден.")
        
class CurrentUserDetailView(generics.RetrieveAPIView): # Или MeView, как было у коллеги
    """
    Возвращает полную информацию (User + Profile) для текущего аутентифицированного пользователя.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().select_related("profile")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    

    
class TopTrainersListView(generics.ListAPIView):
    """
    Возвращает список топ-10 тренеров, отсортированных по их level_score.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = User.objects.filter(profile__role=Profile.Role.TRAINER)\
                               .select_related('profile')\
                               .order_by('-profile__level_score')[:10]
        return queryset
    
    
class AllTrainersListView(generics.ListAPIView):
    """
    List all users with role TRAINER, with pagination, search & ordering.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'username',
        'profile__role',
        'profile__level_score',
    ]
    search_fields = ['username', 'profile__bio']
    ordering_fields = ['username', 'profile__level_score']
    ordering = ['-profile__level_score']

    def get_queryset(self):
        return (
            User.objects
                .filter(profile__role=Profile.Role.TRAINER)
                .select_related('profile')
        )


# --- Admin Actions ---
class AdminUserBlockView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    queryset = Profile.objects.all()

    def post(self, request, pk, *args, **kwargs):
        try:
            profile = Profile.objects.get(user__pk=pk)
            profile.is_blocked = True
            profile.save()
            return Response({"status": "User blocked"}, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(
                {"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND
            )


class AdminUserUnblockView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    queryset = Profile.objects.all()

    def post(self, request, pk, *args, **kwargs):
        try:
            profile = Profile.objects.get(user__pk=pk)
            profile.is_blocked = False
            profile.save()
            return Response({"status": "User unblocked"}, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(
                {"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
