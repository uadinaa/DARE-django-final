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

    // 1. Сохраняем токены в localStorage
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);

    // Отображаем сообщение об успехе
    successMessage.value = 'Вход выполнен успешно! Перенаправление...';
    console.log('Access Token:', accessToken); // Оставляем логи для отладки
    console.log('Refresh Token:', refreshToken);

    // --- УДАЛЕН ВЫЗОВ fetchProfileAndRedirect ---
    // await fetchProfileAndRedirect(accessToken); // <--- УДАЛЕНО

    // Очищаем форму
    formData.username = '';
    formData.password = '';

    // 2. Перенаправляем на главную страницу (с именем роута 'home', который ведет на '/')
    // Небольшая задержка для отображения сообщения
    setTimeout(() => {
      router.push({ name: 'home' });
    }, 1000); // 1 секунда задержки

  } catch (error) {
    if (error.response && error.response.status === 401) {
      errorMessage.value = 'Неверное имя пользователя или пароль.';
    } else if (error.response && error.response.data) {
      const errors = error.response.data; let messages = [];
      for (const key in errors) {
        if (Array.isArray(errors[key])) { messages.push(`${key}: ${errors[key].join(', ')}`); }
        else { messages.push(`${key}: ${errors[key]}`); }
      }
      errorMessage.value = messages.join(' ') || 'Произошла ошибка при входе.';
    } else { errorMessage.value = 'Произошла ошибка сети или сервера.'; }
    console.error('Login error:', error);
    // Если ошибка произошла НЕ при получении токена, а при удаленном fetchProfile,
    // то этот блок catch теперь не будет ловить ошибки 404 оттуда.
  } finally {
    loading.value = false;
  }
};

</script>