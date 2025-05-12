<template>
    <aside class="sidebar">
      <div class="logo-container">
        <router-link to="/">
          <img src="@/assets/logo.svg" alt="Логотип Фитнес-Платформы" class="logo" />
        </router-link>
      </div>
      <nav>
        <ul>
          <li><router-link to="/">Главная</router-link></li>
          <li><router-link :to="{ name: 'profile' }">Мой Профиль</router-link></li>
          <li><router-link to="/chat">Чат-бот</router-link></li>
          <li><router-link to="/settings">Настройки</router-link></li>
        </ul>
      </nav>
      <div class="sidebar-footer">
        <button @click="performLogout" class="logout-button">Выход</button>
      </div>
    </aside>
  </template>
  
  <script setup>
  import { useRouter } from 'vue-router';
  // import apiClient from '@/services/api'; // Раскомментируйте, если будете вызывать API при логауте
  
  const router = useRouter();
  
  const performLogout = async () => {
    // TODO: Реализовать более полную логику логаута с вызовом API и сбросом состояния в store (Pinia/Vuex)
    // const refreshToken = localStorage.getItem('refreshToken');
    // if (refreshToken) {
    //   try {
    //     await apiClient.post('/users/logout/', { refresh: refreshToken });
    //   } catch (error) {
    //     console.error("Server-side logout error:", error);
    //   }
    // }
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    router.push({ name: 'login' });
  };
  </script>
  
  <style scoped>
  .sidebar {
    width: var(--sidebar-width); /* Используем переменную для ширины */
    background-color: var(--vt-c-black-soft); /* Фоновый цвет из переменных */
    color: var(--vt-c-text-dark-1); /* Основной цвет текста */
    padding: 20px 15px;
    display: flex;
    flex-direction: column;
    height: 100vh;
    position: fixed; /* Фиксируем сайдбар */
    left: 0;
    top: 0;
    border-right: 1px solid var(--vt-c-divider-dark-2); /* Более мягкая граница */
    box-shadow: 2px 0 5px rgba(0,0,0,0.1); /* Небольшая тень для глубины */
  }
  
  .logo-container {
    margin-bottom: 40px;
    padding-top: 10px;
    text-align: center;
  }
  
  .logo {
    max-width: 120px;
    height: auto;
  }
  
  nav ul {
    list-style-type: none;
    padding: 0;
    margin: 0;
  }
  
  nav ul li {
    margin-bottom: 8px; /* Немного уменьшим отступ */
  }
  
  nav ul li a {
    color: var(--vt-c-text-dark-2); /* Приглушенный цвет для неактивных ссылок */
    text-decoration: none;
    display: block;
    padding: 10px 15px; /* Уменьшим вертикальные отступы */
    border-radius: 4px; /* Меньше скругление */
    font-weight: 500;
    transition: background-color 0.2s ease, color 0.2s ease;
  }
  
  nav ul li a:hover {
    background-color: var(--vt-c-black-mute); /* Фон при наведении */
    color: var(--vt-c-white); /* Текст при наведении */
  }
  
  nav ul li a.router-link-exact-active {
    background-color: var(--color-accent); /* Акцентный цвет */
    color: var(--vt-c-white); /* Яркий текст для активной ссылки */
    font-weight: 600; /* Чуть жирнее для активного пункта */
  }
  
  .sidebar-footer {
    margin-top: auto; /* Прижимает кнопку вниз */
    padding-top: 20px;
    border-top: 1px solid var(--vt-c-divider-dark-2); /* Более мягкая граница */
  }
  
  .logout-button {
    background-color: transparent;
    color: var(--vt-c-text-dark-2);
    border: 1px solid var(--vt-c-divider-dark-2);
    padding: 10px 15px;
    width: 100%;
    text-align: left;
    border-radius: 4px; /* Меньше скругление */
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
  }
  
  .logout-button:hover {
    background-color: #c0392b; /* Красный цвет при наведении для выхода */
    border-color: #c0392b;
    color: var(--vt-c-white);
  }
  </style>