<template>
    <div class="login-container">
      <h2>Вход</h2>
      <form @submit.prevent="handleLogin">
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
  
        <div class="form-group">
          <label for="login-username">Имя пользователя:</label>
          <input type="text" id="login-username" v-model="formData.username" required>
        </div>
  
        <div class="form-group">
          <label for="login-password">Пароль:</label>
          <input type="password" id="login-password" v-model="formData.password" required>
        </div>
  
        <button type="submit" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive } from 'vue';
  import axios from 'axios';
  
  // Реактивное состояние для данных формы
  const formData = reactive({
    username: '',
    password: '',
  });
  
  const loading = ref(false);
  const errorMessage = ref('');
  const successMessage = ref(''); // Можно добавить сообщение об успешном входе
  
  // URL для получения JWT токенов
  const apiUrl = 'http://localhost:8000/api/token/'; // Эндпоинт для логина
  
  const handleLogin = async () => {
    loading.value = true;
    errorMessage.value = '';
    successMessage.value = '';
  
    try {
      // Отправляем username и password на бэкенд
      const response = await axios.post(apiUrl, {
        username: formData.username,
        password: formData.password,
      });
  
      // Успешный вход - получаем токены
      const accessToken = response.data.access;
      const refreshToken = response.data.refresh;
  
      successMessage.value = 'Вход выполнен успешно!';
      console.log('Access Token:', accessToken);
      console.log('Refresh Token:', refreshToken);
  
      // !! ВАЖНО: Здесь нужно будет сохранить токены !!
      // Например, в localStorage или Vuex/Pinia для дальнейшего использования
      // localStorage.setItem('accessToken', accessToken);
      // localStorage.setItem('refreshToken', refreshToken);
  
      // Очистка формы (опционально)
      formData.username = '';
      formData.password = '';
  
      // TODO: Перенаправить пользователя на другую страницу
      // (потребуется Vue Router)
  
    } catch (error) {
      // Обработка ошибок от API
      if (error.response && error.response.status === 401) {
        // 401 Unauthorized - Неверные учетные данные
        errorMessage.value = 'Неверное имя пользователя или пароль.';
      } else if (error.response && error.response.data) {
         const errors = error.response.data;
         let messages = [];
         for (const key in errors) {
            if(Array.isArray(errors[key])) {
               messages.push(`${key}: ${errors[key].join(', ')}`);
            } else {
               messages.push(`${key}: ${errors[key]}`);
            }
         }
          errorMessage.value = messages.join(' ') || 'Произошла ошибка при входе.';
      }
       else {
        errorMessage.value = 'Произошла ошибка сети или сервера. Попробуйте снова.';
      }
      console.error('Login error:', error);
    } finally {
      loading.value = false;
    }
  };
  </script>
  
  <style scoped>
  /* Стили можно скопировать из RegisterForm.vue или сделать свои */
  .login-container {
    max-width: 400px;
    margin: 50px auto;
    padding: 30px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    background-color: #fff;
    font-family: sans-serif;
  }
  
  h2 {
    text-align: center;
    color: #333;
    margin-bottom: 25px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  label {
    display: block;
    margin-bottom: 8px;
    color: #555;
    font-weight: bold;
  }
  
  input[type="text"],
  input[type="password"] {
    width: 100%;
    padding: 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
    font-size: 1rem;
  }
  
  button {
    width: 100%;
    padding: 12px;
    background-color: #28a745; /* Другой цвет для кнопки входа */
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1.1rem;
    transition: background-color 0.3s ease;
  }
  
  button:hover:not(:disabled) {
    background-color: #218838;
  }
  
   button:disabled {
     background-color: #cccccc;
     cursor: not-allowed;
   }
  
  .error-message {
    color: #dc3545;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 15px;
    text-align: center;
  }
  
  .success-message {
    color: #155724; /* Цвет для успеха */
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 15px;
    text-align: center;
  }
  </style>