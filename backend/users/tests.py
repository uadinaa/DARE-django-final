from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Profile


class UserAuthTests(APITestCase):

    def test_user_registration_success(self):
        """
        Ensure we can register a new user.
        """
        url = reverse("register")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "password2": "password123",
            "role": Profile.Role.USER,  # Регистрируем как обычного пользователя
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "testuser")
        self.assertEqual(
            User.objects.get().profile.role, Profile.Role.USER
        )  # Проверяем роль

    def test_trainer_registration_success(self):
        """
        Ensure we can register a new trainer.
        """
        url = reverse("register")
        data = {
            "username": "testtrainer",
            "email": "trainer@example.com",
            "password": "password123",
            "password2": "password123",
            "role": Profile.Role.TRAINER,  # Регистрируем как тренера
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "testtrainer")
        self.assertTrue(
            User.objects.get().profile.is_trainer
        )  # Проверяем роль через property

    def test_registration_passwords_mismatch(self):
        """
        Ensure registration fails if passwords don't match.
        """
        url = reverse("register")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "password2": "wrongpassword",
            "role": Profile.Role.USER,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_registration_duplicate_username(self):
        """
        Ensure registration fails if username already exists.
        """
        User.objects.create_user(username="existinguser", password="password123")
        url = reverse("register")
        data = {
            "username": "existinguser",
            "email": "test@example.com",
            "password": "password123",
            "password2": "password123",
            "role": Profile.Role.USER,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "username", response.data
        )  # Проверяем, что ошибка связана с username

    def test_login_success(self):
        """
        Ensure user can login and get JWT tokens.
        """
        user = User.objects.create_user(username="loginuser", password="password123")
        url = reverse("token_obtain_pair")  # URL для логина
        data = {"username": "loginuser", "password": "password123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_fail(self):
        """
        Ensure login fails with incorrect credentials.
        """
        User.objects.create_user(username="loginuser", password="password123")
        url = reverse("token_obtain_pair")
        data = {"username": "loginuser", "password": "wrongpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileViewTests(APITestCase):
    def setUp(self):
        # Создаем двух пользователей для тестов
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user1.profile.bio = "Bio for user1"
        self.user1.profile.save()

        self.user2 = User.objects.create_user(username="user2", password="password123")

    def test_get_own_profile_update_view(self):
        """
        Ensure authenticated user can get their own profile update view.
        """
        url = reverse("user-profile-update")
        self.client.force_authenticate(user=self.user1)  # Аутентифицируем user1
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user1.username)
        self.assertEqual(response.data["bio"], "Bio for user1")

    def test_update_own_profile(self):
        """
        Ensure authenticated user can update their own profile (bio, avatar).
        """
        url = reverse("user-profile-update")
        self.client.force_authenticate(user=self.user1)
        new_bio = "Updated bio for user1"
        # Для теста аватара потребуется создать mock-файл
        data = {"bio": new_bio}
        response = self.client.patch(
            url, data, format="json"
        )  # Используем PATCH для частичного обновления
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.profile.refresh_from_db()  # Обновляем объект из БД
        self.assertEqual(self.user1.profile.bio, new_bio)

    def test_cannot_update_other_profile(self):
        """
        Ensure user cannot update another user's profile.
        """
        url = reverse("user-profile-update")
        # user2 пытается обновить профиль user1 - не должно работать,
        # т.к. get_object в UserProfileUpdateView всегда возвращает профиль request.user
        self.client.force_authenticate(user=self.user2)
        data = {"bio": "Trying to update user1 bio"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Статус ОК, но...
        self.user2.profile.refresh_from_db()
        self.user1.profile.refresh_from_db()
        self.assertEqual(
            self.user2.profile.bio, "Trying to update user1 bio"
        )  # ...обновился профиль user2
        self.assertNotEqual(
            self.user1.profile.bio, "Trying to update user1 bio"
        )  # Профиль user1 не изменился

    def test_get_profile_list(self):
        """
        Ensure authenticated user can get the list of profiles.
        """
        url = reverse("profile-list")  # Имя URL из роутера для ProfileViewSet
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что в списке есть оба профиля (или используем пагинацию)
        self.assertTrue(
            len(response.data.get("results", [])) >= 2 or len(response.data) >= 2
        )

    def test_get_profile_detail(self):
        """
        Ensure authenticated user can get profile details.
        """
        url = reverse("profile-detail", kwargs={"pk": self.user1.profile.pk})
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user1.username)
