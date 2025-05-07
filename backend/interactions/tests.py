from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from posts.models import Post
from users.models import Profile

from .models import Comment, Follow, PostLike


class InteractionTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        self.trainer1 = User.objects.create_user(
            username="trainer1", password="password123"
        )
        self.trainer1.profile.role = Profile.Role.TRAINER
        self.trainer1.profile.save()

        self.post_by_trainer = Post.objects.create(
            author=self.trainer1, content="Trainer's post"
        )

    # --- Comment Tests ---
    def test_create_comment(self):
        """
        Ensure authenticated user can comment on a post.
        """
        # URL для комментов к посту trainer1 (/api/posts/{post_pk}/comments/)
        url = reverse("post-comments-list", kwargs={"post_pk": self.post_by_trainer.pk})
        self.client.force_authenticate(user=self.user1)
        data = {"content": "My first comment"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().content, "My first comment")
        self.assertEqual(Comment.objects.get().author, self.user1)
        self.assertEqual(Comment.objects.get().post, self.post_by_trainer)

    def test_list_comments_for_post(self):
        """
        Ensure anyone (even unauthenticated) can list comments for a post.
        """
        Comment.objects.create(
            post=self.post_by_trainer, author=self.user1, content="Comment 1"
        )
        Comment.objects.create(
            post=self.post_by_trainer, author=self.user2, content="Comment 2"
        )
        url = reverse("post-comments-list", kwargs={"post_pk": self.post_by_trainer.pk})
        response = self.client.get(url)  # Не аутентифицируемся
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем наличие комментов (учитывая пагинацию)
        self.assertTrue(
            len(response.data.get("results", [])) >= 2 or len(response.data) >= 2
        )

    def test_delete_own_comment(self):
        """Ensure author can delete their own comment."""
        comment = Comment.objects.create(
            post=self.post_by_trainer, author=self.user1, content="Comment to delete"
        )
        # URL для конкретного коммента: /api/posts/{post_pk}/comments/{comment_pk}/
        url = reverse(
            "post-comments-detail",
            kwargs={"post_pk": self.post_by_trainer.pk, "pk": comment.pk},
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_other_comment_forbidden(self):
        """Ensure user cannot delete another user's comment."""
        comment = Comment.objects.create(
            post=self.post_by_trainer, author=self.user1, content="Other's comment"
        )
        url = reverse(
            "post-comments-detail",
            kwargs={"post_pk": self.post_by_trainer.pk, "pk": comment.pk},
        )
        self.client.force_authenticate(
            user=self.user2
        )  # user2 пытается удалить коммент user1
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 1)

    # --- Like Tests ---
    def test_like_post(self):
        """
        Ensure user can like a post.
        """
        # URL: /api/posts/{post_pk}/like/
        url = reverse("post-like", kwargs={"post_pk": self.post_by_trainer.pk})
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(url)  # POST для лайка
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PostLike.objects.count(), 1)
        self.assertTrue(
            PostLike.objects.filter(user=self.user1, post=self.post_by_trainer).exists()
        )

    def test_like_post_already_liked(self):
        """
        Ensure liking an already liked post returns 200 OK.
        """
        PostLike.objects.create(
            user=self.user1, post=self.post_by_trainer
        )  # Предустановка лайка
        url = reverse("post-like", kwargs={"post_pk": self.post_by_trainer.pk})
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(url)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )  # Ожидаем 200, а не 201
        self.assertEqual(PostLike.objects.count(), 1)  # Убедимся, что дубль не создался

    def test_unlike_post(self):
        """
        Ensure user can unlike a post.
        """
        PostLike.objects.create(
            user=self.user1, post=self.post_by_trainer
        )  # Предустановка лайка
        url = reverse("post-like", kwargs={"post_pk": self.post_by_trainer.pk})
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(url)  # DELETE для анлайка
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PostLike.objects.count(), 0)

    def test_unlike_post_not_liked(self):
        """
        Ensure unliking a post that wasn't liked returns 404.
        """
        url = reverse("post-like", kwargs={"post_pk": self.post_by_trainer.pk})
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Follow Tests ---
    def test_follow_trainer(self):
        """
        Ensure user can follow a trainer.
        """
        # URL: /api/interactions/follow/{user_pk}/
        url = reverse("follow-user", kwargs={"user_pk": self.trainer1.pk})
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Follow.objects.filter(follower=self.user1, followed=self.trainer1).exists()
        )

    def test_follow_already_following(self):
        """Ensure following someone you already follow returns 200 OK."""
        Follow.objects.create(follower=self.user1, followed=self.trainer1)
        url = reverse("follow-user", kwargs={"user_pk": self.trainer1.pk})
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Follow.objects.count(), 1)

    def test_follow_non_trainer_forbidden(self):
        """
        Ensure user cannot follow a non-trainer user.
        """
        url = reverse(
            "follow-user", kwargs={"user_pk": self.user2.pk}
        )  # Пытаемся подписаться на user2
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(url)
        # Ожидаем ошибку валидации или Forbidden, в зависимости от реализации проверки
        self.assertTrue(
            response.status_code
            in [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN]
        )
        self.assertFalse(
            Follow.objects.filter(follower=self.user1, followed=self.user2).exists()
        )

    def test_follow_self_forbidden(self):
        """
        Ensure user cannot follow themselves.
        """
        url = reverse("follow-user", kwargs={"user_pk": self.user1.pk})
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(url)
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )  # Ожидаем ошибку валидации

    def test_unfollow_trainer(self):
        """
        Ensure user can unfollow a trainer.
        """
        Follow.objects.create(
            follower=self.user1, followed=self.trainer1
        )  # Предустановка подписки
        # URL: /api/interactions/unfollow/{user_pk}/
        url = reverse("unfollow-user", kwargs={"user_pk": self.trainer1.pk})
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Follow.objects.filter(follower=self.user1, followed=self.trainer1).exists()
        )

    def test_unfollow_not_following(self):
        """
        Ensure unfollowing someone you don't follow returns 404.
        """
        url = reverse("unfollow-user", kwargs={"user_pk": self.trainer1.pk})
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_following(self):
        """Ensure we can list who a user is following."""
        Follow.objects.create(follower=self.user1, followed=self.trainer1)
        # URL: /api/interactions/users/{user_pk}/following/
        url = reverse("user-following-list", kwargs={"user_pk": self.user1.pk})
        self.client.force_authenticate(user=self.user2)  # user2 смотрит подписки user1
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что trainer1 есть в списке (учитывая пагинацию)
        results = response.data.get(
            "results", response.data
        )  # Учитываем пагинацию или ее отсутствие
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["followed"]["username"], self.trainer1.username)

    def test_list_followers(self):
        """Ensure we can list a trainer's followers."""
        Follow.objects.create(follower=self.user1, followed=self.trainer1)
        Follow.objects.create(follower=self.user2, followed=self.trainer1)
        # URL: /api/interactions/users/{user_pk}/followers/
        url = reverse("user-follower-list", kwargs={"user_pk": self.trainer1.pk})
        self.client.force_authenticate(
            user=self.user1
        )  # user1 смотрит подписчиков trainer1
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 2)
        follower_usernames = {item["follower"]["username"] for item in results}
        self.assertIn(self.user1.username, follower_usernames)
        self.assertIn(self.user2.username, follower_usernames)

    def test_list_followers_of_non_trainer(self):
        """Ensure listing followers of a non-trainer raises PermissionDenied (as implemented)."""
        url = reverse(
            "user-follower-list", kwargs={"user_pk": self.user1.pk}
        )  # Смотрим подписчиков user1
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        # Ожидаем 403 Forbidden, так как мы раскомментировали проверку во view
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
