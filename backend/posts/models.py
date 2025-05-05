from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit 

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(verbose_name='Содержание')
    image = ProcessedImageField(
        upload_to='post_images/',
        processors=[ResizeToFit(width=300, height=300)],
        format='JPEG',
        options={'quality': 80},
        null=True,
        blank=True,
        verbose_name='Изображение'
    )
    # Для простоты сделаем одно изображение и одно видео.
    video = models.FileField(upload_to='post_videos/', null=True, blank=True, verbose_name='Видео')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    def __str__(self):
        return f"Пост от {self.author.username} в {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'