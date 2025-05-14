from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from imagekit import ImageSpec, register
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from django.utils import timezone
import uuid



class Profile(models.Model):
    class Role(models.TextChoices):
        USER = "user", "Пользователь"
        TRAINER = "trainer", "Тренер"
        # Администратор определяется через is_staff/is_superuser в User

    class VerificationStatus(models.TextChoices):
        NONE = "none", "Нет заявки"
        PENDING = "pending", "На рассмотрении"
        APPROVED = "approved", "Одобрено"
        REJECTED = "rejected", "Отклонено"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    bio = models.TextField(blank=True, null=True, verbose_name="О себе")
    avatar = ProcessedImageField(
        upload_to="avatars/",
        processors=[ResizeToFit(width=200, height=200)],
        format="JPEG",
        options={"quality": 85},
        null=True,
        blank=True,
        verbose_name="Аватар",
    )
    is_blocked = models.BooleanField(default=False, verbose_name='Заблокирован')
    can_monetize_posts = models.BooleanField(default=False, verbose_name='Может монетизировать посты')
    level_score = models.IntegerField(default=0, verbose_name='Общий уровень/ранк')
    levels_last_calculated_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата последнего расчета уровней')

    verification_status = models.CharField(
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.NONE,
        verbose_name="Статус верификации"
    )
    identity_document = models.FileField(
        upload_to='verification_documents/identity/',
        null=True, blank=True,
        verbose_name="Документ (Удостоверение)"
    )
    qualification_document = models.FileField(
        upload_to='verification_documents/qualification/',
        null=True, blank=True,
        verbose_name="Документ (Квалификация)"
    )
    verification_requested_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Время последнего запроса верификации"
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()}) - Ver: {self.get_verification_status_display()}"

    @property
    def is_trainer(self):
        return self.role == self.Role.TRAINER

    @property
    def can_request_verification(self):
        if self.role == self.Role.TRAINER: # Уже тренер
            return False
        if self.verification_status == self.VerificationStatus.PENDING: # Заявка уже в обработке
            return False
        if self.verification_status == self.VerificationStatus.REJECTED and self.verification_requested_at:
            # Проверяем, прошло ли 24 часа с момента отклонения
            if timezone.now() < self.verification_requested_at + timezone.timedelta(hours=24):
                return False
        return True

# Сигнал для автоматического создания/обновления профиля при создании/обновлении User
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class VerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    action = models.CharField(max_length=10) # 'approve' или 'reject'
    # Можно добавить срок действия токена, если нужно
    # expires_at = models.DateTimeField()

    def __str__(self):
        return f"Token for {self.user.username} - Action: {self.action}"