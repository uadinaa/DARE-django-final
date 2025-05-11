from django.urls import include, path
from rest_framework_nested import routers

from interactions.views import CommentViewSet, PostLikeCreateDestroyView

from .views import PostViewSet

router = routers.DefaultRouter()
router.register(r"", PostViewSet, basename="post")

# Вложенный роутер для комментариев к постам /api/posts/{post_pk}/comments/
posts_router = routers.NestedDefaultRouter(router, r"", lookup="post")
posts_router.register(r"comments", CommentViewSet, basename="post-comments")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(posts_router.urls)),
    # Отдельный URL для лайка/анлайка поста /api/posts/{post_pk}/like/
    path("<int:post_pk>/like/", PostLikeCreateDestroyView.as_view(), name="post-like"),
]
