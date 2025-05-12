# interactions/models.py
from django.contrib.auth.models import User
from django.db import models

from posts.models import Post  # Импортируем модель Post


class Follow(models.Model):
    follower = models.ForeignKey(
        User, related_name="following", on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        User, related_name="followers", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followed"], name="unique_follow"
            )
        ]
        ordering = ["-created_at"]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.follower.username} -> {self.followed.username}"


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"Комментарий от {self.author.username} к посту {self.post_id}"


class PostLike(models.Model):
    user = models.ForeignKey(User, related_name="post_likes", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_post_like")
        ]
        ordering = ["-created_at"]
        verbose_name = "Лайк поста"
        verbose_name_plural = "Лайки постов"

    def __str__(self):
        return f"{self.user.username} лайкнул пост {self.post_id}"
