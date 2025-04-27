from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from .models import Profile
from .serializers import RegisterSerializer, ProfileSerializer, UserSerializer
from core.permissions import IsProfileOwnerOrAdmin, IsAdminUser

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
     pass

class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated] 

class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrAdmin] # Только владелец или админ

    def get_object(self):
        return self.request.user.profile

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

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
             return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

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
             return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)