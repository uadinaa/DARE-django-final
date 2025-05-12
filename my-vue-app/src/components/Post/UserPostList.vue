<template>
    <div class="user-post-list" ref="scrollComponentPosts">
      <div v-if="initialLoading" class="text-center text-light mt-3">
        <div class="spinner-border text-success spinner-border-sm" role="status"></div>
        <p class="small">Загрузка постов пользователя...</p>
      </div>
      <div v-else-if="error" class="alert alert-warning small">
        Не удалось загрузить посты: {{ error.message }}
      </div>
      <div v-else-if="posts.length">
        <PostItem v-for="post in posts" :key="post.id" :post="post" class="mb-3" />
        <div v-if="loadingMore" class="text-center text-light py-3">
          <div class="spinner-border spinner-border-sm text-success" role="status"></div>
          <p class="mb-0 small">Подгружаем еще посты...</p>
        </div>
        <div v-if="!hasNextPage && posts.length > 0 && !initialLoading && !loadingMore" class="text-center text-muted small py-3">
          Больше постов нет.
        </div>
      </div>
      <p v-else class="text-muted small mt-3">У этого пользователя еще нет постов.</p>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
  import apiClient from '@/services/api';
  import PostItem from '@/components/Post/PostItem.vue';
  
  const props = defineProps({
    userId: {
      type: [String, Number],
      required: true,
    },
  });
  
  const posts = ref([]);
  const initialLoading = ref(true);
  const loadingMore = ref(false);
  const error = ref(null);
  const nextPageUrl = ref(null);
  const scrollComponentPosts = ref(null);
  
  const hasNextPage = computed(() => nextPageUrl.value !== null);
  
  const fetchUserPosts = async (isLoadMore = false) => {
    let endpoint;
    if (isLoadMore) {
      if (!nextPageUrl.value || loadingMore.value) return;
      endpoint = nextPageUrl.value.replace(apiClient.defaults.baseURL, ''); // nextPageUrl уже полный
      loadingMore.value = true;
    } else {
      posts.value = []; // Очищаем для новой загрузки или смены userId
      nextPageUrl.value = null;
      initialLoading.value = true;
      endpoint = `/posts/?author=${props.userId}`; // Фильтруем по автору
    }
    error.value = null;
  
    try {
      const response = await apiClient.get(endpoint);
      const newPosts = response.data.results || response.data; // Учитываем пагинацию
  
      if (isLoadMore) {
        posts.value.push(...newPosts);
      } else {
        posts.value = newPosts;
      }
      nextPageUrl.value = response.data.next || null;
    } catch (err) {
      console.error(`Error fetching posts for user ${props.userId}:`, err);
      error.value = err;
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
    // Отслеживаем скролл всего окна. Если у вас скроллится конкретный div,
    // то нужно будет привязать ref к нему и отслеживать его скролл.
    const el = document.documentElement;
    const nearBottomOfPage = el.scrollTop + el.clientHeight >= el.scrollHeight - 300; // Порог в 300px
  
    if (nearBottomOfPage && hasNextPage.value && !loadingMore.value) {
      fetchUserPosts(true);
    }
  };
  
  onMounted(() => {
    if (props.userId) {
      fetchUserPosts(false);
    }
    window.addEventListener('scroll', handleScroll, true);
  });
  
  onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll, true);
  });
  
  watch(() => props.userId, (newUserId) => {
    if (newUserId) {
      fetchUserPosts(false); // Перезагружаем посты, если ID пользователя изменился
    } else {
      posts.value = []; // Очищаем посты, если userId стал null/undefined
      initialLoading.value = false;
    }
  });
  </script>
  
  <style scoped>
  /* Стили для списка постов пользователя, если нужны */
  .user-post-list {
    width: 100%; /* Занимает доступную ширину в родительском контейнере */
  }
  </style>