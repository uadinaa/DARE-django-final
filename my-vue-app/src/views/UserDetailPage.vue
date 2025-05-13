<template>
  <div class="user-detail-page container py-4">
    <div v-if="loadingPage" class="text-center text-light mt-5">
      <div class="spinner-border text-success" role="status"></div>
      <p>Загрузка профиля...</p>
    </div>
    <div v-else-if="pageError" class="alert alert-danger">
      <p>Ошибка: {{ pageError.message || 'Не удалось загрузить профиль.' }}</p>
      <span v-if="pageError.response && pageError.response.status === 404">Пользователь не найден.</span>
    </div>
    <div v-else-if="userData" class="profile-content">
      <div class="profile-header d-flex align-items-center mb-4">
        <img :src="userData.profile.avatar_url || defaultAvatar" alt="Аватар" class="profile-avatar me-4"/>
        <div class="profile-header-info">
          <h2 class="text-light mb-1">{{ userData.username }}</h2>
          <p class="trainer-level-display mb-2 small">Уровень: {{ userData.profile.level_score || 0 }}</p>
          
          <button 
            v-if="canShowFollowButton" 
            @click="toggleFollow" 
            :class="['btn', 'btn-sm', 'mb-3', isFollowing ? 'btn-outline-light' : 'btn-success']"
            :disabled="followLoading">
            <span v-if="followLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            {{ followLoading ? '...' : (isFollowing ? 'Отписаться' : 'Подписаться') }}
          </button>
        </div>
      </div>

      <div class="profile-bio mb-4">
        <p class="text-light" style="white-space: pre-wrap;">{{ userData.profile.bio || 'Информация о себе отсутствует.' }}</p>
      </div>

      <hr class="border-secondary my-4">

      <div class="profile-stats d-flex justify-content-start gap-4 mb-4">
        <div v-if="userData.profile.role === 'trainer'" class="stat-item">
          <router-link :to="{ name: 'user-followers', params: { userId: userData.id } }" class="stat-link">
            <div class="stat-number">{{ userData.profile.followers_count !== undefined ? userData.profile.followers_count : '...' }}</div>
            <div class="stat-label">Подписчики</div>
          </router-link>
        </div>
        <router-link :to="{ name: 'user-following', params: { userId: userData.id } }" class="stat-link">
          <div class="stat-number">{{ userData.profile.following_count !== undefined ? userData.profile.following_count : '...' }}</div>
          <div class="stat-label">Подписки</div>
        </router-link>
      </div>

      <div v-if="userData.profile.role === 'trainer'" class="user-posts mt-4">
        <h4 class="text-success mb-3">Посты пользователя {{ userData.username }}:</h4>
        <UserPostList :user-id="userData.id" />
      </div>
    </div>

    <div v-if="snackbar.show" :class="['snackbar', snackbar.type === 'success' ? 'bg-success' : 'bg-danger']">
      {{ snackbar.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, reactive } from 'vue';
import { useRoute } from 'vue-router'; // useRouter убран, если не используется для редиректа при ошибке
import apiClient from '@/services/api';
import UserPostList from '@/components/Post/UserPostList.vue';
// import { useAuthStore } from '@/store/auth'; // Предполагается для получения данных текущего пользователя

const props = defineProps({
  userId: { type: [String, Number], required: true }
});

// --- Состояние для текущего аутентифицированного пользователя (заглушка) ---
// В реальном приложении эти данные должны приходить из Pinia/Vuex store
const currentUser = ref({ id: null }); // Например, { id: 1, username: 'testuser1' }
const isLoggedIn = ref(false);
// --------------------------------------------------------------------

const userData = ref(null); // Данные просматриваемого пользователя
const loadingPage = ref(true);
const pageError = ref(null);
const defaultAvatar = '/src/assets/default-avatar.png';

const isFollowing = ref(false); // Подписан ли текущий пользователь на просматриваемого тренера
const followLoading = ref(false); // Для состояния загрузки кнопки подписаться/отписаться

const snackbar = reactive({
  show: false,
  message: '',
  type: 'success' // 'success' или 'error'
});

// Определяем, можно ли показывать кнопку "Подписаться"
const canShowFollowButton = computed(() => {
  return isLoggedIn.value && 
         currentUser.value?.id !== null && 
         userData.value?.id !== null &&
         currentUser.value.id !== userData.value.id && 
         userData.value?.profile?.role === 'trainer';
});

// Функция для показа снекбара
const showSnackbar = (message, type = 'success', duration = 3000) => {
  snackbar.message = message;
  snackbar.type = type;
  snackbar.show = true;
  setTimeout(() => {
    snackbar.show = false;
  }, duration);
};

// Загрузка данных просматриваемого пользователя
const fetchUserProfile = async (id) => {
  if (!id) return;
  loadingPage.value = true; pageError.value = null; userData.value = null;
  try {
    const response = await apiClient.get(`/users/${id}/`);
    userData.value = response.data;
    if (isLoggedIn.value && currentUser.value?.id && userData.value?.profile?.role === 'trainer') {
      await checkFollowStatus(); // Проверяем статус подписки после загрузки данных пользователя
    }
  } catch (err) {
    console.error('Error fetching user profile for ID:', id, err);
    pageError.value = err;
  } finally {
    loadingPage.value = false;
  }
};

// Проверка, подписан ли текущий пользователь на просматриваемого тренера
const checkFollowStatus = async () => {
  if (!isLoggedIn.value || !currentUser.value?.id || !userData.value?.id) {
    isFollowing.value = false;
    return;
  }
  try {
    // Запрашиваем список тех, на кого подписан ТЕКУЩИЙ пользователь
    const response = await apiClient.get(`/interactions/users/${currentUser.value.id}/following/`);
    const followingList = response.data.results || response.data;
    isFollowing.value = followingList.some(follow => follow.followed.id === parseInt(props.userId, 10));
  } catch (error) {
    console.error("Error checking follow status:", error);
    isFollowing.value = false; // По умолчанию, если ошибка
  }
};

// Функция для подписки/отписки
const toggleFollow = async () => {
  if (!canShowFollowButton.value || followLoading.value) return;

  followLoading.value = true;
  const targetUserId = props.userId;

  try {
    if (isFollowing.value) {
      // Отписаться
      await apiClient.delete(`/interactions/unfollow/${targetUserId}/`);
      isFollowing.value = false;
      if (userData.value && userData.value.profile && userData.value.profile.followers_count > 0) {
        userData.value.profile.followers_count--; // Уменьшаем счетчик локально
      }
      showSnackbar('Вы успешно отписались!', 'success');
    } else {
      // Подписаться
      await apiClient.post(`/interactions/follow/${targetUserId}/`);
      isFollowing.value = true;
      if (userData.value && userData.value.profile) {
         // Увеличиваем счетчик, если он уже есть, иначе устанавливаем в 1
        userData.value.profile.followers_count = (userData.value.profile.followers_count || 0) + 1;
      }
      showSnackbar('Вы успешно подписались!', 'success');
    }
  } catch (error) {
    console.error("Error toggling follow:", error);
    showSnackbar('Ошибка при выполнении действия.', 'error');
  } finally {
    followLoading.value = false;
  }
};

onMounted(() => {
  // Получаем ID текущего пользователя (упрощенно, лучше из store)
  const token = localStorage.getItem('accessToken');
  if (token) {
    try {
      const decodedToken = JSON.parse(atob(token.split('.')[1]));
      currentUser.value.id = decodedToken.user_id;
      isLoggedIn.value = true;
    } catch (e) { console.error("Error decoding token:", e); isLoggedIn.value = false; }
  } else {
    isLoggedIn.value = false;
  }
  fetchUserProfile(props.userId);
});

watch(() => props.userId, (newUserId) => {
  if (newUserId) {
    fetchUserProfile(newUserId);
  }
});
</script>

<style scoped>
.user-detail-page { color: var(--vt-c-text-dark-1); }
.profile-avatar { 
  width: 100px; 
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--vt-c-divider-dark-1);
}
.stat-link { color: var(--vt-c-text-dark-1); text-decoration: none; display: inline-block; }
.stat-link:hover .stat-label, .stat-link:hover .stat-number { color: var(--color-accent); }
.stat-number { font-size: 1.5rem; font-weight: bold; line-height: 1.1; }
.stat-label { font-size: 0.9rem; color: var(--vt-c-text-dark-2); }

/* Стили для снекбара */
.snackbar {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 20px;
  color: white;
  border-radius: 5px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  z-index: 1000;
  font-size: 0.9rem;
}
.snackbar.bg-success { 
  background-color: var(--color-accent);
}
.trainer-level-display {
  color: var(--vt-c-white-soft);
  font-size: 0.9em;
}
.snackbar.bg-danger {
  background-color: #dc3545;
}
</style>