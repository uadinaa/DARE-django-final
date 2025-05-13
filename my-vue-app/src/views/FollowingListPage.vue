<template>
  <div class="follow-list-page container py-4" ref="scrollComponent">
    <div class="page-header-profile-lists mb-4">
      <h1 class="text-light page-title me-auto">{{ targetUsername || 'Пользователь' }}</h1>
      <div class="feed-toggle-buttons">
        <router-link
          :to="{ name: 'user-followers', params: { userId: props.userId } }"
          class="btn"
          :class="isActive('user-followers') ? 'btn-success' : 'btn-outline-secondary'"
        >
          Подписчики
        </router-link>
        <router-link
          :to="{ name: 'user-following', params: { userId: props.userId } }"
          class="btn ms-2"
          :class="isActive('user-following') ? 'btn-success' : 'btn-outline-secondary'"
        >
          Подписки
        </router-link>
      </div>
    </div>
    <div v-if="initialLoading && listItems.length === 0" class="text-center text-light mt-5">
      <div class="spinner-border text-success" role="status"></div> Загрузка...
    </div>
    <div v-else-if="pageError" class="alert alert-danger">Ошибка: {{ pageError.message }}</div>
    <div v-else-if="listItems.length">
      <ul class="list-group list-group-flush">
        <li 
          v-for="follow in listItems" 
          :key="follow.id" 
          class="list-group-item mb-2"
        >
          <router-link 
            v-if="follow.followed"
            :to="{ name: 'user-detail', params: { userId: follow.followed.id } }" 
            class="d-flex align-items-center text-decoration-none"
          >
            <img 
              :src="follow.followed.profile?.avatar_url || defaultAvatar" 
              alt="Аватар" 
              class="avatar-xs me-3 rounded-circle"
            >
            <span>{{ follow.followed.username }}</span>
          </router-link>
          <span v-else class="text-muted">Пользователь не найден</span>
          </li>
      </ul>
      <div v-if="loadingMore" class="text-center text-light py-3">
        <div class="spinner-border spinner-border-sm text-success" role="status"></div>
        <p class="mb-0 small">Подгружаем еще...</p>
      </div>
    </div>
    <p v-else-if="!initialLoading" class="text-light">Этот пользователь пока ни на кого не подписан.</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue';
import { useRoute } from 'vue-router'; // Импортируем useRoute
import apiClient from '@/services/api';

const props = defineProps({
  userId: { type: [String, Number], required: true }
});

const route = useRoute(); // Получаем текущий маршрут

const listItems = ref([]); // Будут храниться объекты Follow (те, на кого подписан props.userId)
const initialLoading = ref(true);
const loadingMore = ref(false);
const pageError = ref(null);
const targetUsername = ref(''); 
const defaultAvatar = '/src/assets/default-avatar.png';
const nextPageUrl = ref(null);
const scrollComponent = ref(null);

const hasNextPage = computed(() => nextPageUrl.value !== null);

// Функция для определения активной вкладки
const isActive = (routeName) => {
  return route.name === routeName;
};

const checkAndLoadMore = async () => {
  await nextTick(); 
  const element = scrollComponent.value;
  if (!element) return;
  const contentFitsScreen = element.scrollHeight <= element.clientHeight + 5;
  if (contentFitsScreen && hasNextPage.value && !loadingMore.value) {
    await fetchList(true);
  }
};

const fetchList = async (isLoadMore = false) => {
  let endpoint;
  if (isLoadMore) {
    if (!nextPageUrl.value || loadingMore.value) return;
    endpoint = nextPageUrl.value.replace(apiClient.defaults.baseURL, '');
    loadingMore.value = true;
  } else {
    listItems.value = [];
    nextPageUrl.value = null;
    initialLoading.value = true;
    endpoint = `/interactions/users/${props.userId}/following/`; // Эндпоинт для подписок
    if (!targetUsername.value && props.userId) { // Загружаем имя только один раз
        try {
            const userRes = await apiClient.get(`/users/${props.userId}/`);
            targetUsername.value = userRes.data.username;
        } catch (e) { console.warn("Could not fetch target username for following list", e)}
    }
  }
  pageError.value = null;

  try {
    const response = await apiClient.get(endpoint);
    const results = response.data.results || [];

    if (isLoadMore) {
      listItems.value.push(...results);
    } else {
      listItems.value = results;
    }
    nextPageUrl.value = response.data.next || null;
    await checkAndLoadMore();
  } catch (err) {
    console.error('Error fetching following list:', err);
    pageError.value = err;
    if (err.response && err.response.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
    }
  } finally {
    if (isLoadMore) loadingMore.value = false;
    else initialLoading.value = false;
  }
};

const handleScroll = () => {
  const el = document.documentElement; // или scrollComponent.value
  const nearBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 200;
  if (nearBottom && hasNextPage.value && !loadingMore.value) {
    fetchList(true);
  }
};

onMounted(() => {
  if (props.userId) fetchList(false);
  const scrollTarget = scrollComponent.value;
  if (scrollTarget && scrollTarget.scrollHeight > scrollTarget.clientHeight) {
    scrollTarget.addEventListener('scroll', handleScroll);
  } else {
    window.addEventListener('scroll', handleScroll, true);
  }
});
onUnmounted(() => {
  const scrollTarget = scrollComponent.value;
   if (scrollTarget) {
    scrollTarget.removeEventListener('scroll', handleScroll);
  } else {
    window.removeEventListener('scroll', handleScroll, true);
  }
});
watch(() => props.userId, (newId) => {
  if (newId) {
    targetUsername.value = ''; // Сбрасываем имя, чтобы загрузить для нового user
    fetchList(false);
  }
});
</script>

<style scoped>
/* Стили точно такие же, как для FollowersListPage.vue */
.follow-list-page { 
  color: var(--vt-c-text-dark-1);
}
.avatar-xs { 
  width: 40px; 
  height: 40px; 
  object-fit: cover; 
  border: 1px solid var(--vt-c-divider-dark-1); 
}

.page-header-profile-lists {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--vt-c-divider-dark-1);
  padding-bottom: 1rem;
}
.page-title {
  margin: 0;
  font-size: 1.75rem;
}
.feed-toggle-buttons .btn {
  font-weight: 500;
  font-size: 0.9rem;
}

.list-group-item {
  background-color: var(--color-card-bg-dark) !important;
  border-color: var(--vt-c-divider-dark-2) !important;
  color: var(--vt-c-text-dark-1);
  transition: background-color 0.2s ease-in-out;
  margin-bottom: 0.5rem;
  border-radius: 0.375rem;
  padding: 0.75rem 1rem;
}
.list-group-item a {
  color: var(--vt-c-text-dark-1);
  text-decoration: none;
}
.list-group-item a:hover span {
  color: var(--color-accent) !important; 
}
.list-group-item:hover {
  background-color: var(--vt-c-black-soft) !important; 
}
.list-group.list-group-flush .list-group-item {
  border-width: 0 0 1px;
}
.list-group.list-group-flush .list-group-item:last-child {
  border-bottom-width: 0;
}
</style>