<template>
  <div class="user-detail-page">
    <div v-if="loading" class="text-center text-light mt-5">
      <div class="spinner-border text-success" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p>Загрузка профиля пользователя...</p>
    </div>
    <div v-else-if="error" class="alert alert-danger">
      <p>Ошибка при загрузке профиля: {{ error.message }}</p>
      <p v-if="error.response && error.response.status === 404">
        Пользователь не найден.
      </p>
    </div>
    <div v-else-if="userData" class="user-profile-content">
      <h1 class="text-light mb-4">Профиль: {{ userData.username }}</h1>
      
      <div class="card bg-dark text-light border-secondary">
        <div class="row g-0">
          <div class="col-md-4 text-center p-3">
            <img 
              :src="userData.profile.avatar_url || defaultAvatar" 
              alt="Аватар" 
              class="img-fluid rounded-circle avatar-profile mb-3"
            />
          </div>
          <div class="col-md-8">
            <div class="card-body">
              <h5 class="card-title text-success">{{ userData.username }}</h5>
              <p class="card-text"><small class="text-muted">Роль: {{ userData.profile.role_display }}</small></p>
              <p class="card-text"><strong>О себе:</strong> {{ userData.profile.bio || 'Нет информации' }}</p>
              <p v-if="userData.profile.role === 'trainer'" class="card-text">
                <strong>Уровень тренера:</strong> {{ userData.profile.level_score }}
              </p>
              </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '@/services/api';

const props = defineProps({
  userId: { // Получаем userId из props маршрутизатора
    type: [String, Number],
    required: true,
  },
});

const userData = ref(null);
const loading = ref(true);
const error = ref(null);
const defaultAvatar = ref('/src/assets/default-avatar.png'); // Укажите путь

const fetchUserProfile = async (id) => {
  if (!id) return;
  loading.value = true;
  error.value = null;
  userData.value = null; 
  try {
    const response = await apiClient.get(`/users/${id}/`);
    userData.value = response.data;
  } catch (err) {
    console.error('Error fetching user profile for ID:', id, err);
    error.value = err;
  } finally {
    loading.value = false;
  }
};

// Загружаем данные при монтировании и при изменении props.userId
onMounted(() => {
  fetchUserProfile(props.userId);
});

watch(() => props.userId, (newUserId) => {
  fetchUserProfile(newUserId);
});
</script>

<style scoped>
.user-detail-page {
  padding: 20px;
  color: var(--vt-c-text-dark-1);
}
.avatar-profile {
  width: 180px;
  height: 180px;
  object-fit: cover;
  border: 3px solid var(--vt-c-divider-dark-1);
}
.card-body p {
  margin-bottom: 0.5rem;
}
</style>