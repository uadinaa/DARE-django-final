# users/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        TRAINER = 'trainer', 'Тренер'
        # Администратор определяется через is_staff/is_superuser в User

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    bio = models.TextField(blank=True, null=True, verbose_name='О себе')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Аватар')
    is_blocked = models.BooleanField(default=False, verbose_name='Заблокирован')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_trainer(self):
        return self.role == self.Role.TRAINER

# Сигнал для автоматического создания/обновления профиля при создании/обновлении User
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()