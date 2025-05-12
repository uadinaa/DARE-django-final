<template>
  <div class="profile-page container py-4">
    <div v-if="loading" class="text-center text-light mt-5">
      <div class="spinner-border text-success" role="status"></div>
      <p>Загрузка профиля...</p>
    </div>
    <div v-else-if="error" class="alert alert-danger">Ошибка: {{ error.message }}</div>
    <div v-else-if="user" class="profile-content">
      <div class="profile-header d-flex align-items-center mb-4">
        <img :src="user.profile.avatar_url || defaultAvatar" alt="Аватар" class="profile-avatar me-4"/>
        <div class="profile-header-info">
          <h2 class="text-light mb-1">{{ user.username }}</h2>
          <p class="trainer-level-display mb-2 small">Уровень: {{ user.profile.level_score || 0 }}</p>
          <router-link :to="{ name: 'profile-edit' }" class="btn btn-outline-light btn-sm">
            Редактировать профиль
          </router-link>
        </div>
      </div>

      <div class="profile-bio mb-4">
        <p class="text-light" style="white-space: pre-wrap;">{{ user.profile.bio || 'Информация о себе отсутствует.' }}</p>
      </div>
      
      <hr class="border-secondary my-4">

      <div class="profile-stats d-flex justify-content-start gap-4 mb-4">
        <router-link :to="{ name: 'user-following', params: { userId: user.id } }" class="stat-link">
          <div class="stat-number">{{ followingCount }}</div>
          <div class="stat-label">Подписки</div>
        </router-link>
        <div v-if="user.profile.role === 'trainer'" class="stat-item">
          <router-link :to="{ name: 'user-followers', params: { userId: user.id } }" class="stat-link">
            <div class="stat-number">{{ followersCount }}</div>
            <div class="stat-label">Подписчики</div>
          </router-link>
        </div>
      </div>

      <div v-if="user.profile.role === 'trainer'" class="user-posts mt-4">
        <h4 class="text-success mb-3">Мои посты:</h4>
        <UserPostList :user-id="user.id" />
      </div>
    </div>
    <div v-else class="alert alert-warning">
      Не удалось загрузить данные пользователя.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import UserPostList from '@/components/Post/UserPostList.vue'; // Предполагается, что этот компонент существует

const user = ref(null);
const loading = ref(true);
const error = ref(null);
const defaultAvatar = '/src/assets/default-avatar.png'; // Укажите ваш путь

// Эти значения нужно будет загружать отдельно или получать из user.value, если API их возвращает
const followingCount = ref(0); 
const followersCount = ref(0);

const fetchCurrentUser = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/users/me/'); // Эндпоинт для данных текущего пользователя
    user.value = response.data;
    // Здесь можно добавить запросы для получения followingCount и followersCount
    // Например:
    if (user.value) {
      const followingRes = await apiClient.get(`/interactions/users/${user.value.id}/following/`);
      followingCount.value = followingRes.data.count || (Array.isArray(followingRes.data) ? followingRes.data.length : 0);
      if (user.value.profile.role === 'trainer') {
        const followersRes = await apiClient.get(`/interactions/users/${user.value.id}/followers/`);
        followersCount.value = followersRes.data.count || (Array.isArray(followersRes.data) ? followersRes.data.length : 0);
      }
    }
  } catch (err) {
    console.error('Error fetching current user data:', err);
    error.value = err;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchCurrentUser();
});
</script>

<style scoped>
.profile-page { color: var(--vt-c-text-dark-1); }
.profile-header { /* Стили для основного блока с аватаром и именем */ }
.profile-avatar { 
  width: 100px; /* Размер аватара */
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--vt-c-divider-dark-1);
}
.profile-header-info {
  /* Стили для блока с именем и кнопкой */
}
.profile-bio p {
  margin-bottom: 0; /* Убрать нижний отступ у параграфа с био, если нужно */
}
.trainer-level-display {
  color: var(--vt-c-white-soft);
  font-size: 0.9em;
}
.stat-link { color: var(--vt-c-text-dark-1); text-decoration: none; display: inline-block; }
.stat-link:hover .stat-label, .stat-link:hover .stat-number { color: var(--color-accent); }
.stat-number { font-size: 1.5rem; font-weight: bold; line-height: 1.1; }
.stat-label { font-size: 0.9rem; color: var(--vt-c-text-dark-2); }
.user-posts { /* Стили для блока с постами, если нужны */ }
</style>