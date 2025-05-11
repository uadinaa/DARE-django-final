<template>
    <div class="top-trainers-widget">
      <h5 class="text-light">Топ Тренеров</h5>
      <ul v-if="trainers.length" class="list-unstyled">
        <li v-for="trainer in trainers" :key="trainer.id" class="mb-2">
          <router-link :to="`/users/${trainer.id}`"> {{ trainer.username }} (Уровень: {{ trainer.level_score }})
          </router-link>
        </li>
      </ul>
      <p v-else class="text-muted small">Загрузка списка тренеров...</p>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  // import apiClient from '@/services/api';
  
  const trainers = ref([
    // Заглушки данных
    // { id: 101, username: 'SuperTrainer1', level_score: 150 },
    // { id: 102, username: 'MegaCoach', level_score: 145 },
  ]);
  
  // Пример загрузки (нужно раскомментировать и адаптировать)
  /*
  onMounted(async () => {
    try {
      // const response = await apiClient.get('/users/trainers/top/'); // Пример эндпоинта
      // trainers.value = response.data.results || response.data;
    } catch (error) {
      console.error("Error fetching top trainers:", error);
    }
  });
  */
  </script>
  
  <style scoped>
  .top-trainers-widget {
    padding: 15px;
    background-color: var(--vt-c-black-mute); /* Используем переменную */
    border-radius: 8px;
  }
  .top-trainers-widget h5 {
    margin-bottom: 15px;
    border-bottom: 1px solid var(--vt-c-divider-dark-2);
    padding-bottom: 10px;
  }
  .top-trainers-widget ul li a {
    color: var(--vt-c-text-dark-2);
    text-decoration: none;
  }
  .top-trainers-widget ul li a:hover {
    color: var(--color-accent);
  }
  /* .avatar-sm { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; } */
  </style>