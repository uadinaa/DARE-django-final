<template>
    <div class="profile-edit-page container py-4">
      <h1 class="text-light mb-4">Редактировать профиль</h1>
      <div v-if="loadingProfile" class="text-center text-light"><div class="spinner-border text-success"></div> Загрузка...</div>
      <div v-else-if="profileError" class="alert alert-danger">{{ profileError }}</div>
      <form v-if="formData" @submit.prevent="handleProfileUpdate" class="card bg-dark text-light border-secondary p-4">
        <div class="mb-3">
          <label for="bio" class="form-label">О себе (Био):</label>
          <textarea id="bio" v-model="formData.bio" class="form-control form-control-dark" rows="5"></textarea>
        </div>
        <div class="mb-3">
          <label for="avatar" class="form-label">Новый аватар:</label>
          <input type="file" id="avatar" @change="onFileChange" class="form-control form-control-dark" accept="image/*">
          <div v-if="avatarPreview" class="mt-2">
            <p>Предпросмотр:</p>
            <img :src="avatarPreview" alt="Предпросмотр аватара" class="img-thumbnail" style="max-width: 150px; max-height: 150px;">
          </div>
          <small v-if="currentAvatarUrl" class="d-block mt-2">
            Текущий аватар: <a :href="currentAvatarUrl" target="_blank">смотреть</a>
          </small>
        </div>
         <div class="mb-3 form-check" v-if="isCurrentUserTrainer">
            <input type="checkbox" class="form-check-input" id="canMonetize" v-model="formData.can_monetize_posts">
            <label class="form-check-label" for="canMonetize">Разрешить монетизацию постов</label>
          </div>
  
        <div v-if="updateError" class="alert alert-danger small mt-2">{{ updateError }}</div>
        <div v-if="updateSuccess" class="alert alert-success small mt-2">Профиль успешно обновлен!</div>
  
        <button type="submit" class="btn btn-success mt-3" :disabled="saving">
          {{ saving ? 'Сохранение...' : 'Сохранить изменения' }}
        </button>
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
  const isCurrentUserTrainer = ref(true); 
  
  const formData = reactive({
    bio: '',
    avatar: null, // Для нового файла аватара
    can_monetize_posts: false,
  });
  const avatarPreview = ref(null);
  const currentAvatarUrl = ref(''); // URL текущего аватара для отображения
  
  const loadingProfile = ref(true);
  const profileError = ref('');
  const saving = ref(false);
  const updateError = ref('');
  const updateSuccess = ref(false);
  
  const fetchProfileData = async () => {
    loadingProfile.value = true;
    profileError.value = '';
    try {
      const response = await apiClient.get('/users/me/profile/'); // Эндпоинт для получения текущего профиля
      const profile = response.data;
      formData.bio = profile.bio || '';
      formData.can_monetize_posts = profile.can_monetize_posts || false;
      currentAvatarUrl.value = profile.avatar_url || ''; // Используем avatar_url для отображения
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
      formData.avatar = file; // Сохраняем сам файл для отправки
      // Создаем URL для предпросмотра
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
  
    const dataToUpdate = new FormData(); // Используем FormData для отправки файла
    dataToUpdate.append('bio', formData.bio);
    dataToUpdate.append('can_monetize_posts', formData.can_monetize_posts);
  
    if (formData.avatar) { // Отправляем аватар только если он был выбран
      dataToUpdate.append('avatar', formData.avatar);
    }
  
    try {
      // Отправляем PATCH на эндпоинт обновления профиля текущего пользователя
      await apiClient.patch('/users/me/profile/', dataToUpdate, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      updateSuccess.value = true;
      // authStore.fetchCurrentUser(); // Обновить данные пользователя в store, если используете Pinia
      setTimeout(() => {
        router.push({ name: 'profile' }); // Перенаправляем на страницу профиля
      }, 1500);
    } catch (err) {
      console.error("Error updating profile:", err);
      if (err.response && err.response.data) {
        updateError.value = Object.values(err.response.data).flat().join(' ');
      } else {
        updateError.value = "Произошла ошибка при обновлении профиля.";
      }
    } finally {
      saving.value = false;
    }
  };
  
  onMounted(fetchProfileData);
  </script>
  
  <style scoped>
  .profile-edit-page { color: var(--vt-c-text-dark-1); }
  /* Дополнительные стили, если нужны */
  </style>