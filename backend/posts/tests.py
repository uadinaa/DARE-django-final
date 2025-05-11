from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import Profile

from .models import Post


class PostViewSetTests(APITestCase):
    def setUp(self):
        # Создаем тренера и обычного пользователя
        self.trainer = User.objects.create_user(
            username="trainer1", password="password123"
        )
        self.trainer.profile.role = Profile.Role.TRAINER
        self.trainer.profile.save()

        self.user = User.objects.create_user(username="user1", password="password123")
        # self.user.profile.role остается USER по умолчанию

        self.post1 = Post.objects.create(
            author=self.trainer, content="First post content"
        )
        self.post2 = Post.objects.create(
            author=self.trainer, content="Second post content"
        )

    def test_list_posts_authenticated(self):
        """
        Ensure authenticated user can list posts.
        """
        url = reverse("post-list")  # Имя URL из роутера
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем наличие постов (учитывая пагинацию)
        self.assertTrue(
            len(response.data.get("results", [])) >= 2 or len(response.data) >= 2
        )

    def test_list_posts_unauthenticated_forbidden(self):
        """
        Ensure unauthenticated user CANNOT list posts.
        """
        url = reverse("post-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_as_trainer(self):
        """
        Ensure a trainer can create a post.
        """
        url = reverse("post-list")
        self.client.force_authenticate(user=self.trainer)
        data = {"content": "New post from trainer"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 3)
        self.assertEqual(
            Post.objects.latest("created_at").content, "New post from trainer"
        )
        self.assertEqual(Post.objects.latest("created_at").author, self.trainer)

    def test_create_post_as_regular_user_forbidden(self):
        """
        Ensure a regular user CANNOT create a post.
        """
        url = reverse("post-list")
        self.client.force_authenticate(
            user=self.user
        )  # Аутентифицируем обычного пользователя
        data = {"content": "Post attempt by regular user"}
        response = self.client.post(url, data, format="json")
        # Ожидаем 403 Forbidden, так как IsTrainer пермишн не пройдет
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            Post.objects.count(), 2
        )  # Убедимся, что новый пост не создался

    def test_update_own_post(self):
        """
        Ensure author (trainer) can update their own post.
        """
        url = reverse("post-detail", kwargs={"pk": self.post1.pk})
        self.client.force_authenticate(user=self.trainer)
        data = {"content": "Updated first post content"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.content, "Updated first post content")

    def test_update_other_post_forbidden(self):
        """
        Ensure user cannot update another user's post.
        """
        # Создадим второго тренера и его пост
        other_trainer = User.objects.create_user(
            username="trainer2", password="password123"
        )
        other_trainer.profile.role = Profile.Role.TRAINER
        other_trainer.profile.save()
        other_post = Post.objects.create(
            author=other_trainer, content="Other trainer's post"
        )

        url = reverse("post-detail", kwargs={"pk": other_post.pk})
        self.client.force_authenticate(
            user=self.trainer
        )  # Первый тренер пытается обновить пост второго
        data = {"content": "Attempt to update other's post"}
        response = self.client.patch(url, data, format="json")
        # Ожидаем 403 Forbidden, так как IsAuthorOrReadOnly не пройдет
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_post(self):
        """
        Ensure author (trainer) can delete their own post.
        """
        url = reverse("post-detail", kwargs={"pk": self.post1.pk})
        self.client.force_authenticate(user=self.trainer)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 1)

    def test_delete_other_post_forbidden(self):
        """
        Ensure user cannot delete another user's post.
        """
        other_trainer = User.objects.create_user(
            username="trainer2", password="password123"
        )
        other_trainer.profile.role = Profile.Role.TRAINER
        other_trainer.profile.save()
        other_post = Post.objects.create(
            author=other_trainer, content="Other trainer's post"
        )

        url = reverse("post-detail", kwargs={"pk": other_post.pk})
        self.client.force_authenticate(user=self.trainer)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 3)  # Пост не должен удалиться
