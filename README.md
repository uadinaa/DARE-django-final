# 🏋️‍♂️ Social Fitness Platform

This project includes a **Vue.js** frontend and a **Django** backend.

---

## Link to deployed project
Project is available at [http://139.59.64.140/](http://139.59.64.140/)

---

## 📥 Prerequisites for local launch

Make sure the following are installed:

- [Docker](https://www.docker.com/products/docker-desktop/)
- Docker Compose (usually bundled with Docker Desktop)
- Node.js (≥ 18.x) & npm (for frontend)
- Vue CLI (if used): `npm install -g @vue/cli` (or use `npm run serve` / `npm run dev`)
- Git

---

## 🚀 Installation & Launch Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/uadinaa/DARE-django-final.git
cd DARE-django-final
```

---

### 2. Backend (Django)

The backend runs via Docker Compose (Django + PostgreSQL).

**Navigate to the backend folder**:

```bash
cd backend
```

**Build the image:**

```bash
docker-compose build
```

**Start the containers:**

```bash
docker-compose up -d
```

**Create a superuser (optional):**

```bash
docker-compose exec backend python manage.py createsuperuser
```

**Check:**

- Django: [http://localhost:8000](http://localhost:8000)
- Админка: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

### 3. Frontend (Vue.js)

**Navigate to the frontend folder**:

```bash
cd ../frontend
```

**Install dependencies:**

```bash
npm install
```

**Run the dev server:**

```bash
npm run serve
# или
npm run dev
```

**Check:**

- Vue: [http://localhost:8080](http://localhost:8080) или [http://localhost:5173](http://localhost:5173) (если Vite)

---

## 📚 Описание API Эндпоинтов

**Базовый URL**: `/api`

---

### Authentication (`/api/`)

1. **User register** — `POST /api/users/register/`
2. **Getting JWT token (login)** — `POST /api/token/`
3. **Updating Access token** — `POST /api/token/refresh/`

---

### Users/Trainers and Profiles (`/api/users/`)

4. **List of all users by pagination** — `GET /api/users/`
5. **Current user detail** — `GET /api/users/me/`
6. **Current user profile update/get** — `GET, PUT, PATCH /api/users/me/profile/`
7. **Certain user details** — `GET /api/users/{user_id}/`
8. **List of all trainers** — `GET /api/users/trainers/all/`
9. **Top 10 trainers** — `GET /api/users/trainers/top/`

---

### Posts (`/api/posts/`)

10. **List of all posts** — `GET /api/posts/`
11. **Feed of subscriptions** — `GET /api/posts/subscriptions/`
12. **Post creating** — `POST /api/posts/`
13. **Details/update/delete post** — `GET, PUT, PATCH, DELETE /api/posts/{post_id}/`

---

### Comments (`/api/posts/{post_id}/comments/`)

14. **List of all comments** — `GET /api/posts/{post_id}/comments/`
15. **Comment creating** — `POST /api/posts/{post_id}/comments/`
16. **Details/update/delete comment** — `GET, PUT, PATCH, DELETE /api/posts/{post_id}/comments/{comment_id}/`

---

### Likes (`/api/posts/{post_id}/like/`)

17. **Like/Unlike post** — `POST, DELETE /api/posts/{post_id}/like/`

---

### Subscriptions (`/api/interactions/`)

18. **Subscript to trainer** — `POST /api/interactions/follow/{user_pk}/`
19. **Unsubscript from trainer** — `DELETE /api/interactions/unfollow/{user_pk}/`
20. **List of followings** — `GET /api/interactions/users/{user_pk}/following/`
21. **List of followers** — `GET /api/interactions/users/{user_pk}/followers/`

---

### Admin actions (`/api/users/`)

22. **Block user** — `POST /api/users/{user_pk}/block/`
23. **Unblock user** — `POST /api/users/{user_pk}/unblock/`

---

### Verification (`/api/users/`)

24. **Trainer verification** — `POST /api/users/me/request-trainer-verification/`
25. **Admin verificates trainers** — `POST /api/users/admin/verify-trainer/<int:user_id>/<str:verification_action>/`

---

## 🔒 Notions about auth (JWT)

- **Authorization header:** `Authorization: Bearer <your_access_token>`
- **Refresh token:** use `POST /api/token/refresh/`