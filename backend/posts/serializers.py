from rest_framework import serializers

from users.serializers import UserSerializer

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField(read_only=True)
    is_liked_by_user = serializers.SerializerMethodField(read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "image",
            "created_at",
            "updated_at",
            "likes_count",
            "is_liked_by_user",
            "comments_count",
        ]
        read_only_fields = [
            "id",
            "author",
            "created_at",
            "updated_at",
            "likes_count",
            "is_liked_by_user",
            "comments_count",
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked_by_user(self, obj):
        # Получаем текущего пользователя из контекста запроса
        user = self.context.get("request").user
        # Если пользователь не аутентифицирован, он не мог лайкнуть
        if not user or not user.is_authenticated:
            return False
        # Проверяем, существует ли лайк от этого пользователя для этого поста
        return obj.likes.filter(user=user).exists()
    
    def get_comments_count(self, obj):
        # obj - это экземпляр Post
        # Предполагаем, что у модели Post есть related_name='comments' от модели Comment
        if hasattr(obj, 'comments'):
            return obj.comments.count()
        return 0