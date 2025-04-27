# Training Social Platform

This project includes an Angular frontend and a Django backend.

## 📥 Prerequisites

Ensure the following are installed:

- Python (≥ 3.10)
- Node.js (≥ 18.x) & npm
- Angular CLI: `npm install -g @angular/cli`
- Git

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/uadinaa/DARE-django-final.git
```

### 2. Backend (Django)

1. Go into the backend folder:
    ```bash
    cd backend
    ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

5. Run the Django server:
   ```bash
   python manage.py runserver
   ```

Django is now running at: [http://localhost:8000](http://localhost:8000).

Now open a new terminal window and proceed with frontend setup.

---

### 3. Frontend (Angular)

1. Navigate to the Angular directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Run the Angular development server:
   ```bash
   ng serve
   ```

Angular is now running at: [http://localhost:4200](http://localhost:4200)

---

## API endpoints

## Аутентификация (`/api/`)

### 1. Регистрация пользователя
* **Метод:** `POST`
* **URL:** `/api/users/register/`
* **Описание:** Создает нового пользователя (User) и связанный профиль (Profile).
* **Аутентификация:** Не требуется (`AllowAny`).
* **Request Body (JSON):**
    ```json
    {
      "username": "newuser",
      "email": "new@example.com",
      "password": "password123",
      "password2": "password123",
      "role": "user" // или "trainer"
    }
    ```
* **Response (Успех):** `201 Created`, данные пользователя (без пароля).
* **Response (Ошибка):** `400 Bad Request` (неуникальный username/email, несовпадение паролей и т.д.).

### 2. Получение JWT Токенов (Логин)
* **Метод:** `POST`
* **URL:** `/api/token/`
* **Описание:** Аутентифицирует пользователя по имени и паролю, возвращает `access` и `refresh` JWT токены.
* **Аутентификация:** Не требуется.
* **Request Body (JSON):**
    ```json
    {
      "username": "testuser1",
      "password": "password123"
    }
    ```
* **Response (Успех):** `200 OK`, JSON с токенами:
    ```json
    {
      "refresh": "eyJhbGciOiJ...",
      "access": "eyJhbGciOiJ..."
    }
    ```
* **Response (Ошибка):** `401 Unauthorized`.

### 3. Обновление Access Токена
* **Метод:** `POST`
* **URL:** `/api/token/refresh/`
* **Описание:** Получает новый `access` токен, используя действительный `refresh` токен.
* **Аутентификация:** Не требуется.
* **Request Body (JSON):**
    ```json
    {
      "refresh": "eyJhbGciOiJ..." // Ваш refresh токен
    }
    ```
* **Response (Успех):** `200 OK`, JSON с новым `access` токеном.
* **Response (Ошибка):** `401 Unauthorized`.

---

## Пользователи и Профили (`/api/users/`)

### 4. Список пользователей
* **Метод:** `GET`
* **URL:** `/api/users/`
* **Описание:** Возвращает пагинированный список всех пользователей (основные поля).
* **Аутентификация:** Требуется (`IsAuthenticated`).
* **Response:** `200 OK`.

### 5. Детали пользователя
* **Метод:** `GET`
* **URL:** `/api/users/{user_id}/`
* **Описание:** Возвращает детали конкретного пользователя.
* **Аутентификация:** Требуется (`IsAuthenticated`).
* **Response:** `200 OK`.

### 6. Список профилей
* **Метод:** `GET`
* **URL:** `/api/users/profiles/`
* **Описание:** Возвращает пагинированный список профилей всех пользователей.
* **Аутентификация:** Требуется (`IsAuthenticated`).
* **Response:** `200 OK`.

### 7. Получение/Обновление своего профиля
* **Метод:** `GET`, `PUT`, `PATCH`
* **URL:** `/api/users/profile/`
* **Описание:** `GET` - получить данные своего профиля. `PUT`/`PATCH` - обновить свой профиль (поля `bio`, `avatar`).
* **Аутентификация:** Требуется (`IsAuthenticated`, `IsProfileOwnerOrAdmin` для `PUT`/`PATCH`).
* **Request Body (PATCH, JSON):**
    ```json
    {
      "bio": "Новое описание профиля"
      // "avatar": ... (используйте multipart/form-data для файла)
    }
    ```
* **Response:** `200 OK`, обновленные данные профиля.

---

## Посты (`/api/posts/`)

### 8. Список всех постов
* **Метод:** `GET`
* **URL:** `/api/posts/`
* **Описание:** Возвращает пагинированный список всех постов (тренеров).
* **Аутентификация:** Требуется (`IsAuthenticated`). *Примечание: Если нужно разрешить анонимный просмотр, измените права на `IsAuthenticatedOrReadOnly`.*
* **Response:** `200 OK`.

### 9. Лента подписок
* **Метод:** `GET`
* **URL:** `/api/posts/subscriptions/`
* **Описание:** Возвращает пагинированный список постов только тех тренеров, на которых подписан текущий пользователь.
* **Аутентификация:** Требуется (`IsAuthenticated`).
* **Response:** `200 OK`.

### 10. Создание поста
* **Метод:** `POST`
* **URL:** `/api/posts/`
* **Описание:** Создает новый пост.
* **Аутентификация:** Требуется (`IsAuthenticated`, `IsTrainer`).
* **Request Body:** `multipart/form-data` (если есть файлы) или `application/json`.
    ```json
    {
      "content": "Текст нового поста"
      // "image": файл...,
      // "video": файл...
    }
    ```
* **Response:** `201 Created`, данные созданного поста.

### 11. Детали/Обновление/Удаление поста
* **Метод:** `GET`, `PUT`, `PATCH`, `DELETE`
* **URL:** `/api/posts/{post_id}/`
* **Описание:** `GET` - получить детали поста. `PUT`/`PATCH` - обновить пост. `DELETE` - удалить пост.
* **Аутентификация:** `GET` - `IsAuthenticated`. `PUT`/`PATCH`/`DELETE` - `IsAuthenticated`, `IsAuthorOrReadOnly | IsAdminUser`.
* **Request Body (PUT/PATCH):** JSON или multipart/form-data с обновляемыми полями.
* **Response:** `GET`/`PUT`/`PATCH` - `200 OK`. `DELETE` - `204 No Content`.

---

## Комментарии (`/api/posts/{post_id}/comments/`)

### 12. Список комментариев к посту
* **Метод:** `GET`
* **URL:** `/api/posts/{post_id}/comments/`
* **Описание:** Возвращает пагинированный список комментариев для поста `{post_id}`.
* **Аутентификация:** `IsAuthenticatedOrReadOnly`.
* **Response:** `200 OK`.

### 13. Создание комментария
* **Метод:** `POST`
* **URL:** `/api/posts/{post_id}/comments/`
* **Описание:** Создает новый комментарий к посту `{post_id}`.
* **Аутентификация:** Требуется (`IsAuthenticated`).
* **Request Body (JSON):**
    ```json
    {
      "content": "Текст комментария"
    }
    ```
* **Response:** `201 Created`, данные созданного комментария.

### 14. Детали/Обновление/Удаление комментария
* **Метод:** `GET`, `PUT`, `PATCH`, `DELETE`
* **URL:** `/api/posts/{post_id}/comments/{comment_id}/`
* **Описание:** `GET` - получить детали комментария. `PUT`/`PATCH` - обновить комментарий. `DELETE` - удалить комментарий.
* **Аутентификация:** `GET` - `IsAuthenticatedOrReadOnly`. `PUT`/`PATCH`/`DELETE` - `IsAuthenticated`, `IsAuthorOrReadOnly | IsAdminUser`.
* **Response:** `GET`/`PUT`/`PATCH` - `200 OK`. `DELETE` - `204 No Content`.

---

## Лайки (`/api/posts/{post_id}/like/`)

### 15. Лайк/Анлайк поста
* **Метод:** `POST`, `DELETE`
* **URL:** `/api/posts/{post_id}/like/`
* **Описание:** `POST` - поставить лайк посту `{post_id}`. `DELETE` - убрать лайк.
* **Аутентификация:** Требуется (`IsAuthenticated`).
* **Response:** `POST` - `201 Created` или `200 OK`. `DELETE` - `204 No Content`.

---

## Подписки (`/api/interactions/`)

### 16. Подписаться на пользователя
* **Метод:** `POST`
* **URL:** `/api/interactions/follow/{user_pk}/`
* **Описание:** Подписывает текущего пользователя на пользователя `{user_pk}` (тренера).
* **Аутентификация:** Требуется (`IsAuthenticated`).
* **Response:** `201 Created` или `200 OK`.

### 17. Отписаться от пользователя
* **Метод:** `DELETE`
* **URL:** `/api/interactions/unfollow/{user_pk}/`
* **Описание:** Отписывает текущего пользователя от пользователя `{user_pk}`.
* **Аутентификация:** Требуется (`IsAuthenticated`).
* **Response:** `204 No Content`.

### 18. Список подписок пользователя
* **Метод:** `GET`
* **URL:** `/api/interactions/users/{user_pk}/following/`
* **Описание:** Возвращает список пользователей, на которых подписан пользователь `{user_pk}`.
* **Аутентификация:** Требуется (`IsAuthenticated`).
* **Response:** `200 OK`.

### 19. Список подписчиков пользователя
* **Метод:** `GET`
* **URL:** `/api/interactions/users/{user_pk}/followers/`
* **Описание:** Возвращает список пользователей, которые подписаны на пользователя `{user_pk}` (тренера).
* **Аутентификация:** Требуется (`IsAuthenticated`).
* **Response:** `200 OK`.

---

## Админские действия (`/api/users/`)

*(Эти эндпоинты могут быть не реализованы или доступны только администраторам)*

### 20. Заблокировать пользователя
* **Метод:** `POST`
* **URL:** `/api/users/{user_pk}/block/`
* **Описание:** Блокирует пользователя `{user_pk}`.
* **Аутентификация:** Требуется (`IsAdminUser`).
* **Response:** `200 OK`.

### 21. Разблокировать пользователя
* **Метод:** `POST`
* **URL:** `/api/users/{user_pk}/unblock/`
* **Описание:** Разблокирует пользователя `{user_pk}`.
* **Аутентификация:** Требуется (`IsAdminUser`).
* **Response:** `200 OK`.

---

## Заметки по Аутентификации (JWT)

* **Логин:** Отправьте `POST` запрос на `/api/token/` с `username` и `password`. В ответ получите `access` и `refresh` токены.
* **Аутентифицированные запросы:** Для доступа к защищенным эндпоинтам включайте `access` токен в заголовок каждого запроса: `Authorization: Bearer <your_access_token>`.
* **Обновление токена:** Когда `access` токен истечет (обычно через 60 минут), отправьте `POST` запрос на `/api/token/refresh/` с вашим `refresh` токеном в теле запроса, чтобы получить новый `access` токен.
* **Логаут:** Логаут реализуется на стороне клиента путем удаления сохраненных `access` и `refresh` токенов из хранилища браузера (`localStorage` или `sessionStorage`). На сервере нет специального эндпоинта для логаута (если не настроен черный список токенов).