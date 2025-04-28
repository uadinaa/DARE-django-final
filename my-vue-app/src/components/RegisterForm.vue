<template>
    <div class="register-container">
      <h2>Регистрация</h2>
      <form @submit.prevent="handleRegister">
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
  
        <div class="form-group">
          <label for="username">Имя пользователя:</label>
          <input type="text" id="username" v-model="formData.username" required>
        </div>
  
        <div class="form-group">
          <label for="email">Email:</label>
          <input type="email" id="email" v-model="formData.email" required>
        </div>
  
        <div class="form-group">
          <label for="password">Пароль:</label>
          <input type="password" id="password" v-model="formData.password" required>
        </div>
  
        <div class="form-group">
          <label for="password2">Подтвердите пароль:</label>
          <input type="password" id="password2" v-model="formData.password2" required>
        </div>
  
        <div class="form-group">
          <label for="role">Роль:</label>
          <select id="role" v-model="formData.role" required>
            <option value="user">Пользователь</option>
            <option value="trainer">Тренер</option>
          </select>
        </div>
  
        <button type="submit" :disabled="loading">
          {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
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
    email: '',
    password: '',
    password2: '',
    role: 'user', // Значение по умолчанию
  });
  
  const loading = ref(false);
  const errorMessage = ref('');
  const successMessage = ref('');
  
  // URL вашего бэкенд API (убедитесь, что он правильный)
  // Ваш бэкенд работает на порту 8000 по умолчанию
  const apiUrl = 'http://localhost:8000/api/users/register/';
  
  const handleRegister = async () => {
    loading.value = true;
    errorMessage.value = '';
    successMessage.value = '';
  
    // Простая валидация на фронте (пароли совпадают?)
    if (formData.password !== formData.password2) {
      errorMessage.value = 'Пароли не совпадают.';
      loading.value = false;
      return;
    }
  
    try {
      // Отправляем данные на бэкенд
      // Поля соответствуют RegisterSerializer
      const response = await axios.post(apiUrl, {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        password2: formData.password2,
        role: formData.role, // Отправляем выбранную роль
      });
  
      // Успешная регистрация
      successMessage.value = `Пользователь ${response.data.username} успешно зарегистрирован!`;
      // Очистка формы (опционально)
      formData.username = '';
      formData.email = '';
      formData.password = '';
      formData.password2 = '';
      formData.role = 'user';
  
    } catch (error) {
      // Обработка ошибок от API
      if (error.response && error.response.data) {
        // Пытаемся показать сообщение об ошибке от бэкенда
        const errors = error.response.data;
        let messages = [];
        for (const key in errors) {
          if (Array.isArray(errors[key])) {
             messages.push(`${key}: ${errors[key].join(', ')}`);
          } else {
             messages.push(`${key}: ${errors[key]}`);
          }
        }
        errorMessage.value = messages.join(' ');
      } else {
        errorMessage.value = 'Произошла ошибка при регистрации. Попробуйте снова.';
      }
      console.error('Registration error:', error);
    } finally {
      loading.value = false;
    }
  };
  </script>
  
  <style scoped>
  .register-container {
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
  input[type="email"],
  input[type="password"],
  select {
    width: 100%;
    padding: 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box; /* Учитывает padding и border в ширине */
    font-size: 1rem;
  }
  
  select {
     appearance: none; /* Убрать стандартную стрелку */
     background-color: white;
     background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23007bff%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E');
     background-repeat: no-repeat;
     background-position: right .7em top 50%;
     background-size: .65em auto;
     padding-right: 2em; /* Место для стрелки */
  }
  
  button {
    width: 100%;
    padding: 12px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1.1rem;
    transition: background-color 0.3s ease;
  }
  
  button:hover:not(:disabled) {
    background-color: #0056b3;
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
    color: #28a745;
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 15px;
    text-align: center;
  }
  </style>