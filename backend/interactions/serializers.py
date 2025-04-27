# interactions/serializers.py
from rest_framework import serializers
from .models import Comment, Follow, PostLike
from users.serializers import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'post', 'created_at', 'updated_at']

class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    followed = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed', 'created_at']
        read_only_fields = ['id', 'follower', 'followed', 'created_at']

class PostLikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']