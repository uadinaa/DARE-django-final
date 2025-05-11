// src/views/ProfilePage.vue
<template>
  <div class="profile-page">
    <div v-if="loading" class="text-center text-light mt-5">
      <div class="spinner-border text-success" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p>Загрузка профиля...</p>
    </div>
    <div v-else-if="error" class="alert alert-danger">
      <p>Ошибка при загрузке профиля: {{ error.message }}</p>
    </div>
    <div v-else-if="userData" class="user-profile-content">
      <h1 class="text-light mb-4">Мой профиль: {{ userData.username }}</h1>
      
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
              
              <div v-if="isEditingBio">
                <textarea v-model="editableBio" class="form-control form-control-dark mb-2" rows="3"></textarea>
                <button @click="saveBio" class="btn btn-sm btn-success me-2" :disabled="savingBio">
                  {{ savingBio ? 'Сохранение...' : 'Сохранить Био' }}
                </button>
                <button @click="cancelEditBio" class="btn btn-sm btn-secondary">Отмена</button>
              </div>
              <div v-else>
                <p class="card-text"><strong>О себе:</strong> {{ userData.profile.bio || 'Нет информации' }}</p>
                <button @click="startEditBio" class="btn btn-sm btn-outline-light">Редактировать Био</button>
              </div>

              <p class="card-text mt-3"><strong>Email:</strong> {{ userData.email }}</p>
              <p v-if="userData.profile.role === 'trainer'" class="card-text">
                <strong>Уровень тренера:</strong> {{ userData.profile.level_score }}
              </p>
              <p class="card-text">
                <strong>Может монетизировать посты:</strong> 
                <input type="checkbox" v-model="editableCanMonetize" @change="toggleMonetization" :disabled="savingMonetization">
                {{ userData.profile.can_monetize_posts ? 'Да' : 'Нет' }}
              </p>
              </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="alert alert-warning">
      Не удалось загрузить данные пользователя.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const userData = ref(null);
const loading = ref(true);
const error = ref(null);
const defaultAvatar = ref('/src/assets/default-avatar.png');

const isEditingBio = ref(false);
const editableBio = ref('');
const savingBio = ref(false);

const editableCanMonetize = ref(false);
const savingMonetization = ref(false);

const fetchCurrentUser = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/users/me/');
    userData.value = response.data;
    if (userData.value && userData.value.profile) {
      editableBio.value = userData.value.profile.bio || '';
      editableCanMonetize.value = userData.value.profile.can_monetize_posts || false;
    }
  } catch (err) {
    console.error('Error fetching current user data:', err);
    error.value = err;
  } finally {
    loading.value = false;
  }
};

const startEditBio = () => {
  editableBio.value = userData.value.profile.bio || '';
  isEditingBio.value = true;
};

const cancelEditBio = () => {
  isEditingBio.value = false;
};

const saveBio = async () => {
  if (!userData.value) return;
  savingBio.value = true;
  try {
    const response = await apiClient.patch('/users/me/profile/', { bio: editableBio.value });
    // Обновляем данные в userData, чтобы отобразить изменения
    if (userData.value.profile) {
        userData.value.profile.bio = response.data.bio;
    }
    isEditingBio.value = false;
  } catch (err) {
    console.error('Error updating bio:', err);
    // TODO: Показать сообщение об ошибке пользователю
  } finally {
    savingBio.value = false;
  }
};

const toggleMonetization = async () => {
  if (!userData.value || !userData.value.profile) return;
  savingMonetization.value = true;
  try {
    const response = await apiClient.patch('/users/me/profile/', { can_monetize_posts: editableCanMonetize.value });
     if (userData.value.profile) {
        userData.value.profile.can_monetize_posts = response.data.can_monetize_posts;
    }
  } catch (err) {
    console.error('Error updating monetization status:', err);
    // Вернуть чекбокс в предыдущее состояние в случае ошибки
    if (userData.value && userData.value.profile) {
        editableCanMonetize.value = userData.value.profile.can_monetize_posts;
    }
  } finally {
    savingMonetization.value = false;
  }
};


onMounted(() => {
  fetchCurrentUser();
});
</script>

<style scoped>
.profile-page {
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