# Социальная Фитнес-Платформа

Этот проект включает **Vue.js** фронтенд и **Django** бэкенд.

## 📥 Предварительные требования

Убедитесь, что у вас установлены:

- [Docker](https://www.docker.com/products/docker-desktop/)
- Docker Compose (обычно идет вместе с Docker Desktop)
- Node.js (≥ 18.x) & npm (для фронтенда)
- Vue CLI (если используется): `npm install -g @vue/cli` (или используйте `npm run serve`/`npm run dev`)
- Git

---

## 🚀 Инструкции по установке и запуску

### 1. Клонирование репозитория

```bash
git clone https://github.com/uadinaa/DARE-django-final.git
cd DARE-django-final
```

---

### 2. Бэкенд (Django)

Бэкенд запускается через Docker Compose (Django + PostgreSQL).

Перейдите в папку бэкенда:

```bash
cd backend
```

**Сборка имэджа:**

```bash
docker-compose build
```

**Запуск контейнеров:**

```bash
docker-compose up -d
```

**Создание суперпользователя (опционально):**

```bash
docker-compose exec backend python manage.py createsuperuser
```

**Проверка:**

- Django: [http://localhost:8000](http://localhost:8000)
- Админка: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

### 3. Фронтенд (Vue.js)

Перейдите в папку фронтенда:

```bash
cd ../frontend
```

**Установка зависимостей:**

```bash
npm install
```

**Запуск сервера разработки:**

```bash
npm run serve
# или
npm run dev
```

**Проверка:**

- Vue: [http://localhost:8080](http://localhost:8080) или [http://localhost:5173](http://localhost:5173) (если Vite)

---

## 📚 Описание API Эндпоинтов

**Базовый URL**: `/api`

---

### Аутентификация (`/api/`)

1. **Регистрация пользователя** — `POST /api/users/register/`
2. **Получение JWT токенов (Логин)** — `POST /api/token/`
3. **Обновление Access токена** — `POST /api/token/refresh/`
4. **Logout** — `POST /api/users/logout/`

---

### Пользователи и Профили (`/api/users/`)

5. **Список пользователей** — `GET /api/users/`
6. **Детали пользователя** — `GET /api/users/{user_id}/`
7. **Список профилей** — `GET /api/users/profiles/`
8. **Просмотр/обновление своего профиля** — `GET, PUT, PATCH /api/users/profile/`

---

### Посты (`/api/posts/`)

9. **Список всех постов** — `GET /api/posts/`
10. **Лента подписок** — `GET /api/posts/subscriptions/`
11. **Создание поста** — `POST /api/posts/`
12. **Детали/обновление/удаление поста** — `GET, PUT, PATCH, DELETE /api/posts/{post_id}/`

---

### Комментарии (`/api/posts/{post_id}/comments/`)

13. **Список комментариев** — `GET /api/posts/{post_id}/comments/`
14. **Создание комментария** — `POST /api/posts/{post_id}/comments/`
15. **Детали/обновление/удаление комментария** — `GET, PUT, PATCH, DELETE /api/posts/{post_id}/comments/{comment_id}/`

---

### Лайки (`/api/posts/{post_id}/like/`)

16. **Лайк/Анлайк поста** — `POST, DELETE /api/posts/{post_id}/like/`

---

### Подписки (`/api/interactions/`)

17. **Подписаться на пользователя** — `POST /api/interactions/follow/{user_pk}/`
18. **Отписаться от пользователя** — `DELETE /api/interactions/unfollow/{user_pk}/`
19. **Список подписок пользователя** — `GET /api/interactions/users/{user_pk}/following/`
20. **Список подписчиков пользователя** — `GET /api/interactions/users/{user_pk}/followers/`

---

### Админские действия (`/api/users/`)

21. **Заблокировать пользователя** — `POST /api/users/{user_pk}/block/`
22. **Разблокировать пользователя** — `POST /api/users/{user_pk}/unblock/`

---

## 🔒 Заметки по Аутентификации (JWT)

- **Authorization заголовок:** `Authorization: Bearer <your_access_token>`
- **Обновление токена:** используйте `POST /api/token/refresh/`
- **Logout:** удалите токены на клиенте и отправьте `POST /api/users/logout/` с `refresh` токеном.

---

Хочешь, я ещё сразу подготовлю готовый `.md` файл для скачивания? 🚀  
(Могу сделать его чуть красивее: с оглавлением, якорями, эмодзи для разделов и т.д.) Хочешь?