from django.contrib.auth.models import User
from rest_framework import generics, status, viewsets, filters, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.http import Http404
from django.core.mail import send_mail, EmailMultiAlternatives # Для отправки email
from django.template.loader import render_to_string # Для HTML в письме
from django.conf import settings # Для EMAIL_HOST_USER
from django.urls import reverse # Для генерации ссылок в письме
from django.utils.crypto import get_random_string # Для генерации токенов в ссылках
from rest_framework.views import APIView
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render, get_object_or_404

from core.permissions import IsAdminUser, IsProfileOwnerOrAdmin

from .models import Profile, VerificationToken
from .serializers import ProfileSerializer, RegisterSerializer, UserSerializer, TrainerVerificationRequestSerializer

from django.db.models import Count
from datetime import timedelta
from interactions.models import Follow

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


class RequestTrainerVerificationView(generics.GenericAPIView):
    serializer_class = TrainerVerificationRequestSerializer
    permission_classes = [IsAuthenticated]

    def _create_action_token(self, user, action_type):
        # Remove unused old tokens
        VerificationToken.objects.filter(user=user, action=action_type, is_used=False).delete()
        token_obj = VerificationToken.objects.create(user=user, action=action_type)
        return token_obj.token

    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        if not profile.can_request_verification:
            return Response(
                {"detail": "Вы не можете подать заявку на верификацию в данный момент."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            profile.identity_document = serializer.validated_data['identity_document']
            profile.qualification_document = serializer.validated_data['qualification_document']
            profile.verification_status = Profile.VerificationStatus.PENDING
            profile.verification_requested_at = timezone.now()
            profile.save()

            # Token generation
            approve_token = self._create_action_token(request.user, 'approve')
            reject_token = self._create_action_token(request.user, 'reject')

            # Action URLs
            current_site = get_current_site(request).domain
            approve_url = f"http://{current_site}{reverse('admin-process-verification', kwargs={'user_id_b64': urlsafe_base64_encode(force_bytes(request.user.id)), 'token': approve_token, 'action': 'approve'})}"
            reject_url = f"http://{current_site}{reverse('admin-process-verification', kwargs={'user_id_b64': urlsafe_base64_encode(force_bytes(request.user.id)), 'token': reject_token, 'action': 'reject'})}"

            # Email context
            email_context = {
                'user': request.user,
                'profile': profile,
                'identity_document_url': request.build_absolute_uri(profile.identity_document.url) if profile.identity_document else None,
                'qualification_document_url': request.build_absolute_uri(profile.qualification_document.url) if profile.qualification_document else None,
                'approve_url': approve_url,
                'reject_url': reject_url,
            }

            subject = f"Заявка на верификацию тренера: {request.user.username}"
            text_content = render_to_string('emails/verification_request_admin.txt', email_context)
            html_content = render_to_string('emails/verification_request_admin.html', email_context)

            admin_email = 'eomino1607@gmail.com'
            msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [admin_email])
            msg.attach_alternative(html_content, "text/html")

            try:
                msg.send()
            except Exception as e:
                print(f"Ошибка отправки email: {e}")

            return Response(ProfileSerializer(profile, context={'request': request}).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessTrainerVerificationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id_b64, token, action, *args, **kwargs):
        try:
            user_id = force_str(urlsafe_base64_decode(user_id_b64))
            user = User.objects.get(pk=user_id)
            verification_token = VerificationToken.objects.get(user=user, token=token, action=action, is_used=False)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, VerificationToken.DoesNotExist):
            return render(request, 'verification_result.html', {'message': 'Недействительная или истекшая ссылка для верификации.'})

        profile = user.profile

        if profile.verification_status != Profile.VerificationStatus.PENDING:
            return render(request, 'verification_result.html', {'message': 'Эта заявка уже была обработана.'})

        if action == "approve":
            profile.role = Profile.Role.TRAINER
            profile.verification_status = Profile.VerificationStatus.APPROVED
            message_to_render = f"Заявка пользователя {user.username} на статус тренера одобрена."
            # TODO: Отправить уведомление пользователю об одобрении
        elif action == "reject":
            profile.verification_status = Profile.VerificationStatus.REJECTED
            message_to_render = f"Заявка пользователя {user.username} на статус тренера отклонена."
            # TODO: Отправить уведомление пользователю об отклонении
        else:
            return render(request, 'verification_result.html', {'message': 'Некорректное действие.'})

        profile.save()
        verification_token.is_used = True
        verification_token.save()

        return render(request, 'verification_result.html', {'message': message_to_render})


class AdminVerifyTrainerView(APIView):
    permission_classes = [IsAdminUser] # Только админ

    def post(self, request, user_id, verification_action):
        try:
            user_to_verify = User.objects.get(id=user_id)
            profile_to_verify = user_to_verify.profile
        except (User.DoesNotExist, Profile.DoesNotExist):
            return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

        if profile_to_verify.verification_status != Profile.VerificationStatus.PENDING:
             return Response({"detail": "Заявка не находится в статусе ожидания."}, status=status.HTTP_400_BAD_REQUEST)

        if verification_action == "approve":
            profile_to_verify.role = Profile.Role.TRAINER
            profile_to_verify.verification_status = Profile.VerificationStatus.APPROVED
            # TODO: Отправить уведомление пользователю об одобрении
            profile_to_verify.save()
            return Response({"detail": f"Пользователь {user_to_verify.username} одобрен как тренер."}, status=status.HTTP_200_OK)
        elif verification_action == "reject":
            profile_to_verify.verification_status = Profile.VerificationStatus.REJECTED
            # profile_to_verify.rejection_reason = request.data.get("reason", "Причина не указана.") # Если админ указывает причину
            # TODO: Отправить уведомление пользователю об отклонении
            profile_to_verify.save()
            return Response({"detail": f"Заявка пользователя {user_to_verify.username} отклонена."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Некорректное действие."}, status=status.HTTP_400_BAD_REQUEST)


class TrainerStatsView(generics.RetrieveAPIView):
    """
    Возвращает статистику для текущего авторизованного тренера.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = None  # Или мб можно создать специальный сериализатор для статистики

    def get(self, request, *args, **kwargs):
        trainer = request.user  # Получаем текущего авторизованного пользователя
        # Проверяем тренер? (опционально, но рекомендуется)
        try:
            profile = Profile.objects.get(user=trainer)
            if profile.role != Profile.Role.TRAINER:
                return Response(
                    {"error": "Данный пользователь не является тренером."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Profile.DoesNotExist:
            return Response(
                {"error": "Профиль пользователя не найден."},
                status=status.HTTP_404_NOT_FOUND
            )

        # получаем количество новых подписчиков за последние 7 дней
        today = timezone.now().date()
        dates = [(today - timedelta(days=i)) for i in range(7)]
        dates.reverse()
        dates.reverse()

        daily_counts = []

        for date in dates:
            count = Follow.objects.filter(
                followed=trainer,
                created_at__date=date
            ).count()
            daily_counts.append(count)

        # получаем текущий ранг
        current_rank = profile.level_score

        stats_data = {
            "dailySubscribers": {
                'labels': [date.strftime('%Y-%m-%d') for date in dates],
                'counts': daily_counts
            },
            "currentRank": current_rank,
            # если что здесь можно добавить другие статистические данные
        }

        return Response(stats_data, status=status.HTTP_200_OK)
