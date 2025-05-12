<template>
  <div class="fullscreen-center">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-12 col-sm-10 col-md-8 col-lg-6">
          <div class="card shadow-lg bg-dark text-light border-secondary p-4 p-md-5 rounded-3">
            <h2 class="card-title text-center mb-4 fw-bold">Вход</h2>
            <form @submit.prevent="handleLogin">
              <div v-if="errorMessage" class="alert alert-danger text-center small p-2" role="alert">
                {{ errorMessage }}
              </div>
              <div v-else-if="successMessage" class="alert alert-success text-center small p-2" role="alert">
                {{ successMessage }}
              </div>

              <div class="mb-3">
                <label for="login-username" class="form-label">Имя пользователя:</label>
                <input type="text" id="login-username" class="form-control form-control-dark"
                  v-model="formData.username" required>
              </div>

              <div class="mb-3">
                <label for="login-password" class="form-label">Пароль:</label>
                <input type="password" id="login-password" class="form-control form-control-dark"
                  v-model="formData.password" required>
              </div>

              <button type="submit" :disabled="loading" class="btn btn-success w-100 fw-bold mt-3">
                {{ loading ? 'Вход...' : 'Войти' }}
              </button>
            </form>
            <p class="mt-3 text-center text-muted small d-flex justify-content-center align-items-center">
              <span class="me-1 text-in-span">Еще нет аккаунта?</span>
              <router-link :to="{ name: 'register' }"
                class="btn btn-link btn-sm p-0 align-baseline text-success text-decoration-none fw-bold">
                Зарегистрироваться
              </router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'; // Убрали defineEmits, так как используется router-link
import apiClient from '../services/api.js';
import { useRouter } from 'vue-router';
import { jwtDecode } from 'jwt-decode'; // Убедитесь, что jwt-decode установлен (npm install jwt-decode)

const router = useRouter();

const formData = reactive({ username: '', password: '' });
const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');
// const profileApiUrl = '/api/users/user-profile/'; // Больше не нужно

const handleLogin = async () => {
  loading.value = true;
  errorMessage.value = '';
  successMessage.value = '';
  try {
    const response = await apiClient.post('/token/', {
      username: formData.username,
      password: formData.password,
    });
    const accessToken = response.data.access;
    const refreshToken = response.data.refresh;

    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);

    // --- ДОБАВЛЯЕМ ДЕКОДИРОВАНИЕ И СОХРАНЕНИЕ USER INFO ---
    if (accessToken) {
      try {
        const decodedToken = jwtDecode(accessToken);
        localStorage.setItem('currentUserId', decodedToken.user_id); 
        // Предполагаем, что ваш /api/users/me/ эндпоинт возвращает роль в profile
        // Чтобы получить роль, нужно будет сделать запрос к /users/me/
        // Либо, если ваш JWT токен СОДЕРЖИТ роль, можно извлечь ее оттуда.
        // Для простоты, пока что загрузим роль отдельным запросом или оставим заглушку.
        // ЗАГРУЗКА ПРОФИЛЯ ДЛЯ РОЛИ:
        const userProfileResponse = await apiClient.get('/users/me/', {
            headers: { Authorization: `Bearer ${accessToken}` }
        });
        if (userProfileResponse.data && userProfileResponse.data.profile) {
            localStorage.setItem('currentUserRole', userProfileResponse.data.profile.role);
            // Для админа (is_staff)
            localStorage.setItem('currentUserIsStaff', userProfileResponse.data.is_staff || 'false');
        } else {
            localStorage.removeItem('currentUserRole');
            localStorage.removeItem('currentUserIsStaff');
        }
      } catch (e) {
        console.error("Error decoding token or fetching profile for role:", e);
        localStorage.removeItem('currentUserId');
        localStorage.removeItem('currentUserRole');
        localStorage.removeItem('currentUserIsStaff');
      }
    }
    // ----------------------------------------------------

    successMessage.value = 'Вход выполнен успешно! Перенаправление...';
    
    formData.username = '';
    formData.password = '';

    setTimeout(() => {
      router.push({ name: 'home' });
    }, 1000);

  } catch (error) {
    // ... (обработка ошибок) ...
  } finally {
    loading.value = false;
  }
};
</script>