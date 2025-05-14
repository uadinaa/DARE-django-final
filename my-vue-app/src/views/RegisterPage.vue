<template>
 <div class="fullscreen-center">
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-12 col-sm-10 col-md-8 col-lg-6">
        <div class="card shadow-lg bg-dark text-light border-secondary p-4 p-md-5 rounded-3">
          <h2 class="card-title text-center mb-4 fw-bold">Регистрация</h2>
          <form @submit.prevent="handleRegister">
            <div v-if="errorMessage" class="alert alert-danger text-center small p-2" role="alert">
              {{ errorMessage }}
            </div>
            <div v-if="successMessage" class="alert alert-success text-center small p-2" role="alert">
              {{ successMessage }}
            </div>

            <div class="mb-3">
              <label for="username" class="form-label">Имя пользователя:</label>
              <input type="text" id="username" class="form-control form-control-dark" v-model="formData.username" required>
            </div>

            <div class="mb-3">
              <label for="email" class="form-label">Email:</label>
              <input type="email" id="email" class="form-control form-control-dark" v-model="formData.email" required>
            </div>

            <div class="mb-3">
              <label for="password" class="form-label">Пароль:</label>
              <input type="password" id="password" class="form-control form-control-dark" v-model="formData.password" required>
            </div>

            <div class="mb-3">
              <label for="password2" class="form-label">Подтвердите пароль:</label>
              <input type="password" id="password2" class="form-control form-control-dark" v-model="formData.password2" required>
            </div>

            <button type="submit" :disabled="loading" class="btn btn-success w-100 fw-bold mt-3">
              {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
            </button>
          </form>
          <p class="mt-3 text-center text-muted small d-flex justify-content-center align-items-center">
            <span class="me-1 text-in-span">Уже есть аккаунт?</span>
            <button @click="switchToLogin"  class="btn btn-link btn-sm p-0 align-baseline text-success text-decoration-none fw-bold">
              Войти
            </button>
          </p>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
// --- Скрипт остается тот же ---
import { ref, reactive } from 'vue';
import apiClient from '../services/api.js';
import { useRouter } from 'vue-router';

const router = useRouter();
const formData = reactive({
    username: '', email: '', password: '', password2: '',
});
const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

const handleRegister = async () => {
    loading.value = true; errorMessage.value = ''; successMessage.value = '';
    if (formData.password !== formData.password2) {
        errorMessage.value = 'Пароли не совпадают.'; loading.value = false; return;
    }
    try {
        const response = await apiClient.post('/users/register/', {
             username: formData.username, email: formData.email, password: formData.password,
             password2: formData.password2,
        });
        router.push('/login') // можно по сути сразу после реги перекинуть в логин?
        successMessage.value = `Пользователь ${response.data.username} успешно зарегистрирован!`;
    } catch (error) {
        if (error.response && error.response.data) {
             const errors = error.response.data; let messages = [];
             for (const key in errors) {
                if (Array.isArray(errors[key])) { messages.push(`${key}: ${errors[key].join(', ')}`);}
                else { messages.push(`${key}: ${errors[key]}`); }
             }
             errorMessage.value = messages.join(' ');
        } else { errorMessage.value = 'Произошла ошибка при регистрации.'; }
        console.error('Registration error:', error);
    } finally { loading.value = false; }
};

const switchToLogin = () => {
     router.push('/login');
};
</script>
