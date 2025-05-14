<template>
  <div class="profile-edit-page container py-4">
    <h1 class="text-light mb-4">Редактировать профиль</h1>
    <div v-if="loadingProfile" class="text-center text-light"><div class="spinner-border text-success"></div> Загрузка...</div>
    <div v-else-if="profileError" class="alert alert-danger">{{ profileError }}</div>
    <form v-if="formData && initialUserData" @submit.prevent="handleProfileUpdate" class="card bg-dark text-light border-secondary p-4">
      <div class="mb-3">
        <label for="username" class="form-label">Имя пользователя (нельзя изменить):</label>
        <input type="text" id="username" :value="initialUserData.username" class="form-control form-control-dark" disabled>
      </div>
      <div class="mb-3">
        <label for="email" class="form-label">Email (нельзя изменить):</label>
        <input type="email" id="email" :value="initialUserData.email" class="form-control form-control-dark" disabled>
      </div>
      <div class="mb-3">
        <label for="bio" class="form-label">О себе (Био):</label>
        <textarea id="bio" v-model="formData.bio" class="form-control form-control-dark" rows="5"></textarea>
      </div>
      <div class="mb-3">
        <label for="avatar" class="form-label">Новый аватар:</label>
        <input type="file" id="avatar" @change="onFileChange" class="form-control form-control-dark" accept="image/*">
        <div v-if="avatarPreview" class="mt-2">
          <p class="small text-light">Предпросмотр нового аватара:</p>
          <img :src="avatarPreview" alt="Предпросмотр аватара" class="img-thumbnail" style="max-width: 150px; max-height: 150px;">
        </div>
        <small v-if="currentAvatarUrl && !avatarPreview" class="d-block mt-2 text-light">
          Текущий аватар: <img :src="currentAvatarUrl" alt="Текущий аватар" class="img-thumbnail" style="max-width: 50px; max-height: 50px; vertical-align: middle; margin-left: 5px;">
        </small>
      </div>
       <div class="mb-3 form-check" v-if="isTrainer">
          <input type="checkbox" class="form-check-input" id="canMonetize" v-model="formData.can_monetize_posts">
          <label class="form-check-label" for="canMonetize">Разрешить монетизацию постов</label>
        </div>

      <div v-if="updateError" class="alert alert-danger small mt-2">{{ updateError }}</div>
      <div v-if="updateSuccess" class="alert alert-success small mt-2">Профиль успешно обновлен!</div>

      <button type="submit" class="btn btn-success mt-3" :disabled="saving">
        {{ saving ? 'Сохранение...' : 'Сохранить изменения' }}
      </button>
      <router-link :to="{ name: 'profile' }" class="btn btn-outline-secondary mt-3 ms-2">Отмена</router-link>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import { useRouter } from 'vue-router';
// import { useAuthStore } from '@/store/auth'; // Если используете Pinia

const router = useRouter();
// const authStore = useAuthStore();
// const isCurrentUserTrainer = computed(() => authStore.currentUser?.profile?.role === 'trainer');
// Заглушка для роли, замените на реальную логику из store
const currentUser = ref(null);
const loadingCurrentUser = ref(true);
const isTrainer = computed(() => {
  return currentUser.value && currentUser.value.profile && currentUser.value.profile.role === 'trainer';
});

const initialUserData = ref(null); // Для хранения исходных данных пользователя + профиля
const formData = reactive({ // Для полей, которые можно редактировать
  bio: '',
  avatar: null, 
  can_monetize_posts: false,
});
const avatarPreview = ref(null);
const currentAvatarUrl = ref('');

const loadingProfile = ref(true);
const profileError = ref('');
const saving = ref(false);
const updateError = ref('');
const updateSuccess = ref(false);

const fetchCurrentUser = async () => {
  loadingCurrentUser.value = true;
  try {
    const response = await apiClient.get('/users/me/'); // Эндпоинт для получения данных текущего пользователя
    currentUser.value = response.data;
    // console.log('Current user data:', currentUser.value); // Для отладки
  } catch (error) {
    console.error('Error fetching current user on HomePage:', error);
    currentUser.value = null; // В случае ошибки, пользователь не определен
  } finally {
    loadingCurrentUser.value = false;
  }
};

const fetchProfileData = async () => {
  loadingProfile.value = true;
  profileError.value = '';
  try {
    // Используем эндпоинт /api/users/me/ для получения данных User + Profile
    const response = await apiClient.get('/users/me/'); // <--- ИЗМЕНЕН URL
    initialUserData.value = response.data; // Сохраняем все данные

    if (initialUserData.value && initialUserData.value.profile) {
      // Заполняем редактируемые поля
      formData.bio = initialUserData.value.profile.bio || '';
      formData.can_monetize_posts = initialUserData.value.profile.can_monetize_posts || false;
      currentAvatarUrl.value = initialUserData.value.profile.avatar_url || '';
    } else {
        profileError.value = "Данные профиля неполные.";
    }
  } catch (err) {
    console.error("Error fetching profile data for edit:", err);
    profileError.value = "Не удалось загрузить данные профиля.";
  } finally {
    loadingProfile.value = false;
  }
};

const onFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    formData.avatar = file; 
    const reader = new FileReader();
    reader.onload = (event) => {
      avatarPreview.value = event.target.result;
    };
    reader.readAsDataURL(file);
  } else {
    formData.avatar = null;
    avatarPreview.value = null;
  }
};

const handleProfileUpdate = async () => {
  saving.value = true;
  updateError.value = '';
  updateSuccess.value = false;

  const dataToUpdate = new FormData(); 
  // Отправляем только те поля, которые можно редактировать через этот эндпоинт
  dataToUpdate.append('bio', formData.bio); 
  // Django BooleanField ожидает 'true'/'false' или не отправлять, если не изменилось.
  // Для простоты можно всегда отправлять, если у вас PATCH.
  // Либо формировать dataToUpdate только с измененными полями.
  if (initialUserData.value.profile.can_monetize_posts !== formData.can_monetize_posts) {
      dataToUpdate.append('can_monetize_posts', formData.can_monetize_posts);
  }
  
  if (formData.avatar) { 
    dataToUpdate.append('avatar', formData.avatar);
  }

  try {
    // Отправляем PATCH на эндпоинт обновления профиля текущего пользователя
    // URL: /api/users/me/profile/
    await apiClient.patch('/users/me/profile/', dataToUpdate, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    updateSuccess.value = true;
    // authStore.fetchCurrentUser(); // Обновить данные пользователя в store
    setTimeout(() => {
      router.push({ name: 'profile' }); 
    }, 1500);
  } catch (err) {
    console.error("Error updating profile:", err);
    if (err.response && err.response.data) {
      let messages = [];
      for (const key in err.response.data) {
          if (Array.isArray(err.response.data[key])) {
              messages.push(`${key}: ${err.response.data[key].join(', ')}`);
          } else {
              messages.push(`${key}: ${err.response.data[key]}`);
          }
      }
      updateError.value = messages.join('; ') || "Произошла ошибка при обновлении профиля.";
    } else {
      updateError.value = "Произошла ошибка сети или сервера при обновлении профиля.";
    }
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  fetchProfileData();
  fetchCurrentUser();
});
</script>

<style scoped>
.profile-edit-page { color: var(--vt-c-text-dark-1); }
.img-thumbnail { border: 1px solid var(--vt-c-divider-dark-1); }
</style>