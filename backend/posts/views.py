from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Post
from .serializers import PostSerializer
from core.permissions import IsTrainer, IsAuthorOrReadOnly, IsAdminUser

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author__profile').prefetch_related('likes', 'comments').all()
    serializer_class = PostSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'likes_count']
    search_fields = ['content', 'author__username']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action == 'create':
            # Только тренер может создавать пост
            permission_classes = [permissions.IsAuthenticated, IsTrainer]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Редактировать/удалять может автор ИЛИ админ
            permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly | IsAdminUser]
        else:
            # Читать могут все аутентифицированные
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # Дополнительный action для ленты подписок
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        followed_users = user.following.values_list('followed_id', flat=True)
        queryset = self.filter_queryset(self.get_queryset().filter(author_id__in=followed_users))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)