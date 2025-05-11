<template>
  <div class="home-page" ref="scrollComponent"> <div class="page-header mb-4">
      <h1 class="text-light page-title">Лента</h1>
      <div class="feed-toggle-buttons">
        <button 
          @click="setActiveFeed('all')" 
          :class="['btn', activeFeed === 'all' ? 'btn-success' : 'btn-outline-secondary']">
          Все посты
        </button>
        <button 
          @click="setActiveFeed('subscriptions')" 
          :class="['btn', activeFeed === 'subscriptions' ? 'btn-success' : 'btn-outline-secondary', 'ms-2']">
          Мои подписки
        </button>
      </div>
    </div>

    <CreatePostForm v-if="isTrainer" class="mb-4" @post-created="prependNewPost"/>

    <div v-if="initialLoading" class="text-center text-light mt-5"> <div class="spinner-border text-success" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p>Загрузка постов...</p>
    </div>

    <div v-if="error" class="alert alert-danger mt-3">
      <p>Ошибка при загрузке постов:</p>
      <pre>{{ error.message }}</pre>
      <p v-if="error.response && error.response.data">
        Детали: {{ JSON.stringify(error.response.data) }}
      </p>
    </div>

    <div v-if="!initialLoading && !error && posts.length === 0" class="alert alert-info mt-3">
      Пока нет ни одного поста в этой ленте.
    </div>

    <div v-if="posts.length > 0" class="posts-list">
      <PostItem v-for="post in posts" :key="post.id" :post="post" />
    </div>

    <div v-if="loadingMore" class="text-center text-light py-3">
      <div class="spinner-border spinner-border-sm text-success" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p class="mb-0 small">Подгружаем еще посты...</p>
    </div>
     <div v-if="!hasNextPage && posts.length > 0 && !initialLoading" class="text-center text-muted small py-3">
      Больше постов нет.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import apiClient from '@/services/api.js';
import PostItem from '@/components/Post/PostItem.vue';
import CreatePostForm from '@/components/Post/CreatePostForm.vue';
// import { useAuthStore } from '@/store/auth';

// const authStore = useAuthStore();
// const isTrainer = computed(() => authStore.isLoggedIn && authStore.user?.profile?.role === 'trainer');
const isTrainer = ref(true); // Заглушка

const posts = ref([]);
const initialLoading = ref(true); // Для первоначальной загрузки
const loadingMore = ref(false); // Для подгрузки постов
const error = ref(null);
const activeFeed = ref('all');
const nextPageUrl = ref(null); // URL для следующей страницы
const hasNextPage = computed(() => nextPageUrl.value !== null);

const scrollComponent = ref(null); // Ref для элемента, скролл которого отслеживаем

const fetchPosts = async (isLoadMore = false) => {
  if (!isLoadMore) { // Если это первая загрузка (или смена фильтра)
    initialLoading.value = true;
    posts.value = []; // Очищаем старые посты
    nextPageUrl.value = null; // Сбрасываем URL следующей страницы
  } else { // Если это подгрузка
    if (!nextPageUrl.value || loadingMore.value) return; // Не загружаем, если нет URL или уже идет загрузка
    loadingMore.value = true;
  }
  error.value = null;
  
  const endpoint = isLoadMore ? nextPageUrl.value : (activeFeed.value === 'all' ? '/posts/' : '/posts/subscriptions/');

  try {
    // Если это подгрузка, nextPageUrl уже содержит полный URL, включая /api/
    // Если первая загрузка, apiClient добавит /api/
    const requestUrl = isLoadMore ? endpoint.replace(apiClient.defaults.baseURL, '') : endpoint;
    const response = await apiClient.get(requestUrl);
    
    if (isLoadMore) {
      posts.value.push(...(response.data.results || [])); // Добавляем новые посты к существующим
    } else {
      posts.value = response.data.results || response.data;
    }
    nextPageUrl.value = response.data.next || null; // Сохраняем URL следующей страницы
  } catch (err) {
    console.error(`Ошибка при загрузке постов (${activeFeed.value}):`, err);
    error.value = err;
    if (err.response && err.response.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
    }
  } finally {
    if (!isLoadMore) initialLoading.value = false;
    if (isLoadMore) loadingMore.value = false;
  }
};

const setActiveFeed = (feedType) => {
  if (activeFeed.value !== feedType) {
    activeFeed.value = feedType;
    // fetchPosts() будет вызван через watch, так как isLoadMore = false
  }
};

watch(activeFeed, () => {
  fetchPosts(false); // Первая загрузка для нового типа ленты
});

const prependNewPost = (newPost) => {
  // Добавляем новый пост в начало, если активна лента "Все посты"
  // или если это пост от тренера, на которого мы подписаны (более сложная логика)
  if (activeFeed.value === 'all') {
    posts.value.unshift(newPost);
  } else {
    // Для ленты подписок можно просто перезагрузить первую страницу, 
    // чтобы не усложнять проверку принадлежности поста
    fetchPosts(false); 
  }
};

// Логика отслеживания скролла
const handleScroll = () => {
  // Отслеживаем скролл всего окна, если scrollComponent не определен или это body/html
  // Для более точного контроля можно повесить на конкретный скроллящийся div
  const element = scrollComponent.value || document.documentElement;
  const nearBottomOfPage = element.scrollTop + element.clientHeight >= element.scrollHeight - 200; // За 200px до конца

  if (nearBottomOfPage && hasNextPage.value && !loadingMore.value) {
    fetchPosts(true); // Загружаем следующую страницу
  }
};

onMounted(() => {
  fetchPosts(false); // Первоначальная загрузка
  window.addEventListener('scroll', handleScroll, true); // Отслеживаем скролл на window
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll, true);
});

</script>

<style scoped>
.home-page {
  /* padding-bottom: 50px; /* Добавляем отступ снизу, чтобы индикатор загрузки был виден */
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--vt-c-divider-dark-1);
  padding-bottom: 1rem;
  /* Можно сделать его "липким", если нужно */
  /* position: sticky;
  top: 0; 
  background-color: var(--color-background-dark); /* Фон такой же как у body */
  /* z-index: 10; */
}

.page-title {
  margin: 0;
}

.feed-toggle-buttons .btn {
  font-weight: 500;
}

.posts-list {
  max-width: 700px; 
  margin: 0 auto;
}
</style>