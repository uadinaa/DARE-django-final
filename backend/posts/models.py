# posts/models.py
from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(verbose_name='Содержание')
    image = models.ImageField(upload_to='post_images/', null=True, blank=True, verbose_name='Изображение')
    # Для простоты пока сделаем одно изображение и одно видео.
    # Для нескольких изображений понадобится отдельная модель или ManyToManyField.
    video = models.FileField(upload_to='post_videos/', null=True, blank=True, verbose_name='Видео')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    def __str__(self):
        return f"Пост от {self.author.username} в {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'