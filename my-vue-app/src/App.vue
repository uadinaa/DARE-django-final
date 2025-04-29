<script setup>
import { ref } from 'vue'; // Импортируем ref для состояния
import RegisterForm from './components/RegisterForm.vue';
import LoginForm from './components/LoginForm.vue'; // Импортируем компонент входа

// Состояние для определения, какую форму показывать
const showLogin = ref(false); // По умолчанию показываем регистрацию
</script>

<template>
  <header>
    <img alt="Vue logo" class="logo" src="./assets/logo.svg" width="125" height="125" />
     <div class="nav-buttons">
       <button @click="showLogin = false" :class="{ active: !showLogin }">Регистрация</button>
       <button @click="showLogin = true" :class="{ active: showLogin }">Вход</button>
     </div>
  </header>

  <main>
    <LoginForm v-if="showLogin" />
    <RegisterForm v-else />
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
  margin-bottom: 2rem;
  display: flex; /* Добавим flex для лого и кнопок */
  flex-direction: column; /* Лого сверху, кнопки снизу */
  align-items: center; /* Центрируем все */
}

.logo {
  display: block;
  margin: 0 auto 1rem; /* Отступ снизу для лого */
}

 /* Стили для кнопок переключения */
.nav-buttons {
   display: flex;
   gap: 10px; /* Расстояние между кнопками */
   margin-bottom: 1rem;
}

.nav-buttons button {
   padding: 8px 15px;
   border: 1px solid #ccc;
   background-color: #f8f9fa;
   cursor: pointer;
   border-radius: 4px;
   transition: background-color 0.2s, border-color 0.2s;
}

.nav-buttons button:hover {
   background-color: #e9ecef;
}

.nav-buttons button.active {
   background-color: #007bff;
   color: white;
   border-color: #007bff;
}

main {
   padding: 1rem;
}

/* Медиа-запросы можно оставить или настроить */
@media (min-width: 1024px) {
   header {
       /* На больших экранах можно вернуть лого слева, кнопки справа */
       flex-direction: row;
       justify-content: space-between; /* Разносим лого и кнопки */
       padding-right: calc(var(--section-gap) / 2);
   }
    .logo {
       margin: 0 2rem 0 0; /* Отступ справа для лого */
   }
    .nav-buttons {
       margin-bottom: 0; /* Убираем нижний отступ на больших экранах */
   }
   main {
      padding: 2rem;
   }
}
</style>