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
              <input
                type="text"
                id="login-username"
                class="form-control form-control-dark"
                v-model="formData.username"
                required
              >
            </div>

            <div class="mb-3">
              <label for="login-password" class="form-label">Пароль:</label>
              <input
                type="password"
                id="login-password"
                class="form-control form-control-dark"
                v-model="formData.password"
                required
              >
            </div>

            <button
              type="submit"
              :disabled="loading"
              class="btn btn-success w-100 fw-bold mt-3">
              {{ loading ? 'Вход...' : 'Войти' }}
            </button>
          </form>
           <p class="mt-3 text-center text-muted small d-flex justify-content-center align-items-center">
             <span class="me-1 text-in-span">Еще нет аккаунта?</span>
             <button @click="switchToRegister" class="btn btn-link btn-sm p-0 align-baseline text-success text-decoration-none fw-bold">
               Зарегистрироваться
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
import { ref, reactive, defineEmits } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();

const formData = reactive({ username: '', password: '' });
const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');
const apiUrl = 'http://ec2-13-53-50-251.eu-north-1.compute.amazonaws.com:8000/api/token/';
const profileApiUrl = '/api/users/user-profile/';

const handleLogin = async () => {
    loading.value = true; errorMessage.value = ''; successMessage.value = '';
    try {
        const response = await axios.post(apiUrl, {
            username: formData.username,
            password: formData.password,
        });
        const accessToken = response.data.access;
        const refreshToken = response.data.refresh;
        successMessage.value = 'Вход выполнен успешно!';
        await fetchProfileAndRedirect(accessToken);
        console.log('Access Token:', accessToken);
        console.log('Refresh Token:', refreshToken);

    } catch (error) {
         if (error.response && error.response.status === 401) {
           errorMessage.value = 'Неверное имя пользователя или пароль.';
        } else if (error.response && error.response.data) {
            const errors = error.response.data; let messages = [];
             for (const key in errors) {
               if(Array.isArray(errors[key])) { messages.push(`${key}: ${errors[key].join(', ')}`); }
               else { messages.push(`${key}: ${errors[key]}`); }
             }
             errorMessage.value = messages.join(' ') || 'Произошла ошибка при входе.';
         } else { errorMessage.value = 'Произошла ошибка сети или сервера.'; }
        console.error('Login error:', error);
    } finally { loading.value = false; }
};

const fetchProfileAndRedirect = async (accessToken) => {
     try {
       const profileResponse = await axios.get(profileApiUrl, {
         headers: { Authorization: `Bearer ${accessToken}` }
       });
       const userRole = profileResponse.data.role;

       let targetRoute = '/user-profile'; // Default route
       if (userRole === 'trainer') {
         targetRoute = '/trainer-profile';
       } else if (userRole === 'admin') {
         targetRoute = '/admin-profile';
       }

       router.push(targetRoute);

     } catch (profileError) {
       console.error('Error fetching profile:', profileError);
       errorMessage.value = 'Ошибка при получении профиля.';
       //  Optionally, you might want to redirect to a generic error page or stay on login
     }
};


const switchToRegister = () => {
     router.push('/register');
};


</script>




