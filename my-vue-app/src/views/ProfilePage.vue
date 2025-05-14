<template>
  <div class="profile-page container py-4">
    <div v-if="loading" class="text-center text-light mt-5">
      <div class="spinner-border text-success" role="status"></div>
      <p class="mt-2">Загрузка профиля...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger_custom">
      Ошибка: {{ error }}
    </div>

    <div v-else-if="user" class="profile-content">
      <div class="profile-header d-flex align-items-center mb-4">
        <img :src="user.profile?.avatar_url || defaultAvatar" alt="Аватар" class="profile-avatar me-4"/>
        <div class="profile-header-info">
          <h2 class="text-light mb-1">{{ user.username }}</h2>

          <p class="trainer-level-display mb-2 small">Уровень: {{ user.profile?.level_score || 0 }}</p>
          <div class="d-flex flex-wrap gap-2 align-items-center">
            <router-link
              v-if="isOwnProfile"
              :to="{ name: 'profile-edit' }"
              class="btn btn-outline-light btn-sm"
            >
              Редактировать профиль
            </router-link>

            <div v-if="user.profile?.role === 'trainer'" class="stats">
              <router-link :to="{ name: 'users-stats', params: { userId: user.id } }" class="btn btn-outline-light btn-sm">
                Моя статистика
              </router-link>
            </div>

            <template v-if="isOwnProfile && user.profile?.role !== 'trainer'">
              <button
                v-if="user.profile?.verification_status === 'pending'"
                class="btn btn-secondary btn-sm"
                disabled
              >
                Запрос в обработке
              </button>
              <button
                v-else-if="user.profile?.verification_status === 'rejected' && !user.profile?.can_request_verification_status"
                class="btn btn-warning btn-sm"
                disabled
                title="Повторная заявка будет доступна позже"
              >
                Заявка отклонена
              </button>
              <button
                v-else
                class="btn btn-success btn-sm"
                @click="goToVerificationPage"
                :disabled="!user.profile?.can_request_verification_status"
              >
                {{ (user.profile?.verification_status === 'rejected' && user.profile?.can_request_verification_status) ? 'Подать заявку снова' : 'Стать тренером' }}
              </button>
            </template>
          </div>
           <div v-if="isOwnProfile && user.profile?.role !== 'trainer'" class="mt-2">
              <p v-if="user.profile?.verification_status === 'pending'" class="text-warning small mb-0">
                Ваша заявка на получение статуса тренера находится на рассмотрении.
              </p>
              <p v-if="user.profile?.verification_status === 'rejected' && !user.profile?.can_request_verification_status" class="text-info small mb-0">
                Повторную заявку можно будет подать через некоторое время.
              </p>
               <p v-if="user.profile?.verification_status === 'rejected' && user.profile?.can_request_verification_status" class="text-danger small mb-0">
                Прошлая заявка была отклонена.
              </p>
            </div>
             <div v-if="isOwnProfile && user.profile?.role === 'trainer'" class="mt-2">
                <p class="text-success small mb-0">Вы подтвержденный тренер.</p>
            </div>
        </div>
      </div>

      <div class="profile-bio mb-4">
        <h5 class="text-light">О себе:</h5>
        <p class="text-light" style="white-space: pre-wrap;">{{ user.profile?.bio || 'Информация о себе отсутствует.' }}</p>
      </div>

      <hr class="border-secondary my-4">

      <div class="profile-stats d-flex justify-content-start gap-4 mb-4">
        <div v-if="user.profile?.role === 'trainer'" class="stat-item">
          <router-link :to="{ name: 'user-followers', params: { userId: user.id } }" class="stat-link">
            <div class="stat-number">{{ user.profile?.followers_count ?? followersCount }}</div>
            <div class="stat-label">Подписчики</div>
          </router-link>
        </div>
        <router-link :to="{ name: 'user-following', params: { userId: user.id } }" class="stat-link">
          <div class="stat-number">{{ user.profile?.following_count ?? followingCount }}</div>
          <div class="stat-label">Подписки</div>
        </router-link>
      </div>

      <div v-if="user.profile?.role === 'trainer'" class="user-posts mt-4">
        <h4 class="text-success mb-3">Мои посты:</h4>
        <UserPostList :user-id="user.id" />
      </div>
    </div>

    <div v-else-if="!loading && !user" class="alert alert-warning_custom">
      Не удалось загрузить данные пользователя.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import { jwtDecode } from 'jwt-decode'; // Для определения ID текущего пользователя
import UserPostList from '@/components/Post/UserPostList.vue'; // Предполагается, что этот компонент существует


const route = useRoute();
const router = useRouter();
const user = ref(null); // Переименовал userProfile в user для соответствия существующему коду
const loading = ref(true);
const error = ref(null);
const defaultAvatar = ref('@/assets/default-avatar.png'); // Используем импортированный путь

// Эти значения теперь берем из user.profile, если они там есть, иначе оставляем старые ref для обратной совместимости или если API их не всегда шлет
const followingCount = ref(0); // Будет использоваться, если user.profile.following_count нет
const followersCount = ref(0); // Будет использоваться, если user.profile.followers_count нет
const currentUserId = ref(null); // ID текущего аутентифицированного пользователя

// Определяем, просматривается ли собственный профиль
const isOwnProfile = computed(() => {
  // Если это маршрут 'profile', то это точно свой профиль.
  // Если это 'user-detail', сравниваем ID.
  if (route.name === 'profile') return true;
  return user.value && currentUserId.value && user.value.id === currentUserId.value;
});

// Функция для загрузки данных пользователя (как своего, так и чужого)
const fetchUserData = async () => {
  loading.value = true;
  error.value = null;
  try {
    let response;
    // Если это маршрут для своего профиля (например, /profile)
    if (route.name === 'profile' || (route.params.userId && Number(route.params.userId) === currentUserId.value)) {
      response = await apiClient.get('/users/me/');
    }
    // Если это маршрут для просмотра профиля другого пользователя
    else if (route.params.userId) {
      response = await apiClient.get(`/users/${route.params.userId}/`);
    } else {
      throw new Error("Не удалось определить ID пользователя для загрузки профиля.");
    }
    user.value = response.data;

    // Обновляем счетчики подписчиков/подписок из профиля, если они там есть
    // Иначе оставляем старую логику с отдельными запросами (можно будет убрать, если ProfileSerializer всегда их возвращает)
    if (user.value && user.value.profile) {
      followingCount.value = user.value.profile.following_count ?? 0; // Используем оператор нулевого слияния
      followersCount.value = user.value.profile.followers_count ?? 0;
    } else if (user.value) { // Если вдруг profile пуст, но user есть (маловероятно с вашим API)
        // Можно оставить старую логику с отдельными запросами, но лучше убедиться, что profile всегда приходит
        const followingRes = await apiClient.get(`/interactions/users/${user.value.id}/following/`);
        followingCount.value = followingRes.data.count || (Array.isArray(followingRes.data) ? followingRes.data.length : 0);
        if (user.value.profile?.role === 'trainer') {
            const followersRes = await apiClient.get(`/interactions/users/${user.value.id}/followers/`);
            followersCount.value = followersRes.data.count || (Array.isArray(followersRes.data) ? followersRes.data.length : 0);
        }
    }

  } catch (err) {
    console.error('Error fetching user data:', err);
    error.value = err.response?.data?.detail || err.message || "Произошла ошибка при загрузке профиля.";
    user.value = null; // Сбрасываем пользователя в случае ошибки
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    try {
      const decoded = jwtDecode(token);
      currentUserId.value = decoded.user_id;
    } catch (e) {
      console.error("Error decoding token:", e);
      error.value = "Ошибка аутентификации. Пожалуйста, войдите снова.";
      loading.value = false;
      // router.push({ name: 'login' }); // Можно перенаправить на логин
      return;
    }
  } else {
     error.value = "Вы не авторизованы.";
     loading.value = false;
    //  router.push({ name: 'login' }); // Перенаправить на логин, если токена нет
     return;
  }

  fetchUserData();
});

// Следим за изменением параметра userId в маршруте, чтобы перезагрузить данные, если пользователь переходит между профилями
watch(
  () => route.params.userId,
  (newUserId, oldUserId) => {
    // Перезагружаем, только если newUserId существует (т.е. это user-detail)
    // и он отличается от старого, или если мы перешли на user-detail с другого типа страницы
    if (newUserId && newUserId !== oldUserId && route.name === 'user-detail') {
      fetchUserData();
    }
  }
);
// Также следим за изменением имени маршрута, если пользователь переходит с /users/ID на /profile
watch(
  () => route.name,
  (newName) => {
    if (newName === 'profile' && user.value?.id !== currentUserId.value) { // Если перешли на свой профиль, а отображен чужой
      fetchUserData();
    }
  }
);


const goToVerificationPage = () => {
  router.push({ name: 'become-trainer-verification' }); // Убедись, что маршрут с таким именем существует
};
</script>

<style scoped>
.profile-page { color: var(--vt-c-text-dark-1); }
.profile-avatar {
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--vt-c-divider-dark-1);
}
.profile-header { /* Стили для основного блока с аватаром и именем */ }


.profile-header-info {
  /* Добавляем немного пространства между кнопками, если они в одну строку */
}
.profile-header-info .btn {
  margin-right: 10px; /* Отступ справа для кнопок */
  margin-bottom: 5px; /* Отступ снизу для кнопок, если они переносятся */
}
.profile-header-info .btn:last-child {
  margin-right: 0;
}
.trainer-level-display {
  color: var(--vt-c-white-soft);
  font-size: 0.9em;
}
.stat-link { color: var(--vt-c-text-dark-1); text-decoration: none; display: inline-block; }
.stat-link:hover .stat-label, .stat-link:hover .stat-number { color: var(--color-accent); }
.stat-number { font-size: 1.5rem; font-weight: bold; line-height: 1.1; }
.stat-label { font-size: 0.9rem; color: var(--vt-c-text-dark-2); }

.alert-danger_custom { /* Твои стили для ошибок */
    color: #f8d7da;
    background-color: #4e2227;
    border-color: #f5c6cb;
    font-size: 0.9em;
}
.alert-warning_custom {
    color: #fff3cd;
    background-color: #664d03;
    border-color: #ffecb5;
    font-size: 0.9em;
}
.text-success { color: var(--color-accent) !important; }
.text-warning { color: #ffc107 !important; } /* Bootstrap warning color */
.text-danger { color: #dc3545 !important; } /* Bootstrap danger color */
.text-info { color: #0dcaf0 !important; }   /* Bootstrap info color */

.user-posts { /* Стили для блока с постами, если нужны */ }
</style>
