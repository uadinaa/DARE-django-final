# interactions/views.py
from rest_framework import viewsets, permissions, status, generics, serializers
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Comment, Follow, PostLike
from posts.models import Post
from .serializers import CommentSerializer, FollowSerializer, PostLikeSerializer
from core.permissions import IsAuthorOrReadOnly, IsAdminUser
from rest_framework.exceptions import PermissionDenied

class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Comments.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly | IsAdminUser]

    def get_queryset(self):
        # Возвращаем комментарии только для конкретного поста (если post_pk передан в URL)
        # или все комменты (для админки, например)
        post_pk = self.kwargs.get('post_pk')
        if post_pk:
             return Comment.objects.filter(post_id=post_pk).select_related('author__profile')
        return Comment.objects.select_related('author__profile').all() # Для вложенных роутеров не нужно

    def perform_create(self, serializer):
        # post_pk должен быть в URL (используем вложенные роутеры)
        post = get_object_or_404(Post, pk=self.kwargs.get('post_pk'))
        serializer.save(author=self.request.user, post=post)

# --- Follow Views ---
class FollowCreateView(generics.CreateAPIView):
    """
    API endpoint to follow a user (trainer). Returns 201 if created, 200 if already exists.
    """
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Follow.objects.all()

    def create(self, request, *args, **kwargs):
        follower = request.user
        followed_user_id = self.kwargs.get('user_pk')
        followed_user = get_object_or_404(User.objects.select_related('profile'), pk=followed_user_id)

        # Проверки
        if follower == followed_user:
            raise serializers.ValidationError("You cannot follow yourself.")
        if not followed_user.profile.is_trainer:
             raise PermissionDenied("You can only follow trainers.")

        follow, created = Follow.objects.get_or_create(
            follower=follower,
            followed=followed_user
        )

        # Сериализуем результат
        serializer = self.get_serializer(follow)
        headers = self.get_success_headers(serializer.data)

        # Определяем статус код на основе флага 'created'
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK

        return Response(serializer.data, status=status_code, headers=headers)


class FollowDestroyView(generics.DestroyAPIView):
    """
    API endpoint to unfollow a user.
    """
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        followed_user_id = self.kwargs.get('user_pk') # user_pk из URL
        follower = self.request.user
        return get_object_or_404(Follow, follower=follower, followed_id=followed_user_id)

class FollowingListView(generics.ListAPIView):
    """
    API endpoint to list users followed by a specific user (user_pk from URL).
    """
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated] # Доступно аутентифицированным

    def get_queryset(self):
        # Получаем user_pk из URL
        user_pk = self.kwargs.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)
        # Возвращаем список тех, на кого подписан user_pk
        return Follow.objects.filter(follower=user).select_related('followed__profile')

class FollowerListView(generics.ListAPIView):
    """
    API endpoint to list followers of a specific user (user_pk from URL).
    Optionally restricted to only show followers for trainers.
    """
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated] # Доступно аутентифицированным

    def get_queryset(self):
        # Получаем user_pk из URL
        user_pk = self.kwargs.get('user_pk')
        # Загружаем пользователя вместе с профилем одним запросом
        user = get_object_or_404(User.objects.select_related('profile'), pk=user_pk)

        # Разрешать смотреть подписчиков только у тренеров
        if not user.profile.is_trainer:
            #  Если пользователь не тренер, возвращаем пустой список или ошибку
            raise PermissionDenied("Only trainers have followers viewable via this endpoint.")

        # Возвращаем список подписчиков user_pk
        return Follow.objects.filter(followed=user).select_related('follower__profile')


# --- Like Views ---
class PostLikeCreateDestroyView(generics.GenericAPIView):
     queryset = PostLike.objects.all()
     serializer_class = PostLikeSerializer
     permission_classes = [permissions.IsAuthenticated]

     def post(self, request, *args, **kwargs):
         post_pk = self.kwargs.get('post_pk')
         post = get_object_or_404(Post, pk=post_pk)
         like, created = PostLike.objects.get_or_create(user=request.user, post=post)
         if created:
             serializer = self.get_serializer(like)
             return Response(serializer.data, status=status.HTTP_201_CREATED)
         else:
             # Уже лайкнут, просто возвращаем 200 ОК
             serializer = self.get_serializer(like)
             return Response(serializer.data, status=status.HTTP_200_OK)

     def delete(self, request, *args, **kwargs):
         post_pk = self.kwargs.get('post_pk')
         post = get_object_or_404(Post, pk=post_pk)
         like = get_object_or_404(PostLike, user=request.user, post=post)
         like.delete()
         return Response(status=status.HTTP_204_NO_CONTENT)