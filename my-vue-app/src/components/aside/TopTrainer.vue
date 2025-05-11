// src/components/aside/TopTrainer.vue
<template>
  <div class="top-trainers-widget">
    <h5 class="widget-title">Топ Тренеров</h5>
    <div v-if="loading" class="text-center text-muted small py-3">
      <div class="spinner-border spinner-border-sm" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger_custom small p-2">
      Не удалось загрузить список тренеров.
    </div>
    <ul v-else-if="trainers.length" class="list-unstyled">
      <li v-for="trainer in trainers" :key="trainer.id" class="trainer-item mb-3">
        <router-link :to="{ name: 'user-detail', params: { userId: trainer.id } }" class="trainer-link d-flex align-items-center">
          <img 
            :src="trainer.profile.avatar_url || defaultAvatar" 
            alt="Аватар" 
            class="avatar-sm me-2"
          />
          <div class="trainer-info">
            <span class="trainer-username">{{ trainer.username }}</span>
            <span class="trainer-level d-block text-muted small">Уровень: {{ trainer.profile.level_score }}</span>
          </div>
        </router-link>
      </li>
    </ul>
    <p v-else class="text-muted small py-3">Пока нет топ тренеров.</p>
  </div>
</template>

<script setup>
// ... (script setup остается таким же, как в вашем последнем примере) ...
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const trainers = ref([]);
const loading = ref(true);
const error = ref(null);
const defaultAvatar = ref('/src/assets/default-avatar.png'); 

const fetchTopTrainers = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/users/trainers/top/');
    trainers.value = response.data.results || response.data; 
  } catch (err) {
    console.error("Error fetching top trainers:", err);
    error.value = err;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchTopTrainers();
});
</script>

<style scoped>
/* ... (стили остаются такими же) ... */
.top-trainers-widget {
  padding: 15px;
  background-color: var(--vt-c-black-mute); /* Используем переменную из base.css */
  border-radius: 8px;
}
.widget-title {
  color: var(--vt-c-text-dark-1); /* Используем переменную */
  margin-bottom: 15px;
  border-bottom: 1px solid var(--vt-c-divider-dark-2); /* Используем переменную */
  padding-bottom: 10px;
  font-size: 1.1rem;
}
.trainer-link {
  color: var(--vt-c-text-dark-2);
  text-decoration: none;
  transition: background-color 0.2s ease;
  padding: 8px;
  border-radius: 6px;
  display: flex; 
  align-items: center; 
}
.trainer-link:hover {
  background-color: var(--vt-c-black-soft); 
  color: var(--color-accent); 
}
.avatar-sm {
  width: 40px; 
  height: 40px;
  border-radius: 50%;
  object-fit: cover; 
  border: 1px solid var(--vt-c-divider-dark-1); 
}
.trainer-info {
  display: flex;
  flex-direction: column;
}
.trainer-username {
  font-weight: 500;
}
.trainer-level {
  font-size: 0.85em;
}
.alert-danger_custom {
  color: #f8d7da;
  background-color: #4e2227;
  border-color: #f5c6cb;
  font-size: 0.9em;
}
</style>