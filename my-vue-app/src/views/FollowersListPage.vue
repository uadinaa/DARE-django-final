<template>
    <div class="follow-list-page container py-4" ref="scrollComponent">
      <h1 class="text-light mb-4">Подписчики {{ targetUsername || 'пользователя' }}</h1>
      <div v-if="initialLoading && listItems.length === 0" class="text-center text-light mt-5">
        <div class="spinner-border text-success" role="status"></div> Загрузка...
      </div>
      <div v-else-if="pageError" class="alert alert-danger">
        Ошибка: {{ pageError.message }}
        <span v-if="pageError.response && pageError.response.status === 403">
          Вы не можете просматривать подписчиков этого пользователя.
        </span>
      </div>
      <div v-else-if="listItems.length">
        <ul class="list-group">
          <li v-for="follow in listItems" :key="follow.id" class="list-group-item bg-dark text-light border-secondary mb-2 d-flex align-items-center justify-content-between">
            <router-link 
              v-if="follow.follower"
              :to="{ name: 'user-detail', params: { userId: follow.follower.id } }" 
              class="d-flex align-items-center text-decoration-none text-light flex-grow-1"
            >
              <img 
                :src="follow.follower.profile?.avatar_url || defaultAvatar" 
                alt="Аватар" 
                class="avatar-xs me-3 rounded-circle"
              >
              <span>{{ follow.follower.username }}</span>
            </router-link>
            <span v-else class="text-muted">Пользователь не найден</span>
            </li>
        </ul>
        <div v-if="loadingMore" class="text-center text-light py-3">
          <div class="spinner-border spinner-border-sm text-success" role="status"></div>
          <p class="mb-0 small">Подгружаем еще...</p>
        </div>
         <div v-if="!hasNextPage && listItems.length > 0 && !initialLoading && !loadingMore" class="text-center text-muted small py-3">
          Больше подписчиков нет.
        </div>
      </div>
      <p v-else-if="!initialLoading" class="text-light">У этого пользователя пока нет подписчиков.</p>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted, watch, computed, nextTick, reactive } from 'vue';
  import apiClient from '@/services/api';
  
  const props = defineProps({
    userId: { type: [String, Number], required: true }
  });
  
  const listItems = ref([]); // Будут храниться объекты Follow (где этот user - followed)
  const initialLoading = ref(true);
  const loadingMore = ref(false);
  const pageError = ref(null);
  const targetUsername = ref(''); 
  const defaultAvatar = '/src/assets/default-avatar.png'; // Укажите ваш путь
  const nextPageUrl = ref(null);
  const scrollComponent = ref(null);
  
  const hasNextPage = computed(() => nextPageUrl.value !== null);
  
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
      endpoint = `/interactions/users/${props.userId}/followers/`; // Эндпоинт для подписчиков
      if (!targetUsername.value && props.userId) {
          try {
              const userRes = await apiClient.get(`/users/${props.userId}/`);
              targetUsername.value = userRes.data.username;
          } catch (e) { console.warn("Could not fetch target username", e)}
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
      console.error('Error fetching followers list:', err);
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
    // Привязываем слушатель скролла к самому элементу компонента, если он скроллируемый,
    // или к window, если скроллится вся страница.
    const scrollTarget = scrollComponent.value;
    if (scrollTarget && scrollTarget.scrollHeight > scrollTarget.clientHeight) { // Если есть что скроллить в самом блоке
      scrollTarget.addEventListener('scroll', handleScroll);
    } else { // Иначе слушаем скролл окна
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
      targetUsername.value = '';
      fetchList(false);
    }
  });
  </script>
  
  <style scoped>
  .follow-list-page { 
    color: var(--vt-c-text-dark-1); 
    /* Если хотите скролл внутри этого блока: */
    /* max-height: calc(100vh - 80px); /* Высота минус хедер/другие элементы */
    /* overflow-y: auto; */
  }
  .avatar-xs { 
    width: 40px; 
    height: 40px; 
    object-fit: cover; 
    border: 1px solid var(--vt-c-divider-dark-1); 
  }
  .list-group-item a:hover span { 
    color: var(--color-accent); 
  }
  .list-group-item { 
    transition: background-color 0.2s ease-in-out; 
  }
  .list-group-item:hover { 
    background-color: var(--vt-c-black-soft) !important; 
  }
  </style>