# interactions/urls.py
from django.urls import path
from .views import (
    FollowCreateView,
    FollowDestroyView,
    FollowingListView,
    FollowerListView
)

urlpatterns = [
    path('follow/<int:user_pk>/', FollowCreateView.as_view(), name='follow-user'),
    path('unfollow/<int:user_pk>/', FollowDestroyView.as_view(), name='unfollow-user'),
    path('users/<int:user_pk>/following/', FollowingListView.as_view(), name='user-following-list'),
    path('users/<int:user_pk>/followers/', FollowerListView.as_view(), name='user-follower-list'),
]