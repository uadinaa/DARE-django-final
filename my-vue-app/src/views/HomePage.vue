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

    <CreatePostForm v-if="isTrainer" class="mb-4" @post-created="handlePostCreatedLocally"/>

    <div v-if="initialLoading && posts.length === 0" class="text-center text-light mt-5">
      <div class="spinner-border text-success" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p>Загрузка постов...</p>
    </div>

    <div v-if="pageError" class="alert alert-danger mt-3">
      <p>Ошибка при загрузке постов:</p>
      <pre>{{ pageError.message }}</pre>
      <p v-if="pageError.response && pageError.response.data">
        Детали: {{ JSON.stringify(pageError.response.data) }}
      </p>
    </div>

    <div v-if="!initialLoading && !pageError && posts.length === 0" class="alert alert-info mt-3">
      Пока нет ни одного поста в этой ленте.
    </div>

    <div v-if="posts.length > 0" class="posts-list">
      <div v-for="(post, index) in posts" :key="post.id" class="post-wrapper">
        <PostItem 
          :post="post"
          :is-last-item="index === posts.length - 1" 
          @post-deleted="handlePostDeleted"
          @follow-status-changed="handleFollowStatusChanged"
          @like-status-changed="handleLikeStatusChanged"
        />
      </div>
    </div>

    <div v-if="loadingMore" class="text-center text-light py-3">
      <div class="spinner-border spinner-border-sm text-success" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p class="mb-0 small">Подгружаем еще посты...</p>
    </div>
     <div v-if="!hasNextPage && posts.length > 0 && !initialLoading && !loadingMore" class="text-center text-muted small py-3">
      Больше постов нет.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue';
import apiClient from '@/services/api.js'; // Убедитесь, что путь правильный
import PostItem from '@/components/Post/PostItem.vue';
import CreatePostForm from '@/components/Post/CreatePostForm.vue';
// import { useAuthStore } from '@/store/auth'; // Если используете Pinia

// const authStore = useAuthStore();
// const isTrainer = computed(() => authStore.isLoggedIn && authStore.user?.profile?.role === 'trainer');
const currentUser = ref(null);
const loadingCurrentUser = ref(true);
const isTrainer = computed(() => {
  return currentUser.value && currentUser.value.profile && currentUser.value.profile.role === 'trainer';
});

const posts = ref([]);
const initialLoading = ref(true);
const loadingMore = ref(false);
const pageError = ref(null); // Переименовал error в pageError для ясности
const activeFeed = ref('all'); // 'all' или 'subscriptions'
const nextPageUrl = ref(null);
const scrollComponent = ref(null); // Ref для основного контейнера страницы (или window)

const hasNextPage = computed(() => nextPageUrl.value !== null);

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

const checkAndLoadMore = async () => {
  await nextTick();
  // Отслеживаем скролл всего окна, если не задан конкретный скроллируемый элемент
  const element = document.documentElement; // Используем documentElement для скролла всего окна
  const contentFitsScreen = element.scrollHeight <= element.clientHeight + 5;

  // console.log(`checkAndLoadMore: scrollHeight=${element.scrollHeight}, clientHeight=${element.clientHeight}, contentFitsScreen=${contentFitsScreen}, hasNextPage=${hasNextPage.value}, loadingMore=${loadingMore.value}`);

  if (contentFitsScreen && hasNextPage.value && !loadingMore.value) {
    // console.log("Content fits screen, but more pages exist. Fetching more (checkAndLoadMore)...");
    await fetchPosts(true);
  }
};

const fetchPosts = async (isLoadMore = false) => {
  let endpoint;
  if (isLoadMore) {
    if (!nextPageUrl.value || loadingMore.value) return;
    endpoint = nextPageUrl.value.replace(apiClient.defaults.baseURL, ''); // nextPageUrl уже полный
    loadingMore.value = true;
  } else {
    initialLoading.value = true; // Показываем начальный лоадер
    posts.value = [];
    nextPageUrl.value = null;
    endpoint = activeFeed.value === 'all' ? '/posts/' : '/posts/subscriptions/';
  }
  pageError.value = null;

  try {
    const response = await apiClient.get(endpoint);
    const results = response.data.results || []; // Убедимся, что results это массив

    if (isLoadMore) {
      posts.value.push(...results);
    } else {
      posts.value = results;
    }
    nextPageUrl.value = response.data.next || null;

    // После обновления данных, проверяем, не нужно ли загрузить еще
    // Это особенно важно для первой загрузки, если постов мало
    if (!isLoadMore) { // Только для первоначальной загрузки или смены фильтра
        await checkAndLoadMore();
    }

  } catch (err) {
    console.error(`Ошибка при загрузке постов (${activeFeed.value}):`, err);
    pageError.value = err;
    if (err.response && err.response.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      // TODO: Добавить более изящный редирект через router, если authStore используется
      window.location.href = '/login';
    }
  } finally {
    if (isLoadMore) loadingMore.value = false;
    else initialLoading.value = false;
  }
};

const setActiveFeed = (feedType) => {
  if (activeFeed.value !== feedType) {
    activeFeed.value = feedType;
    // fetchPosts() будет вызван через watch
  }
};

watch(activeFeed, () => {
  fetchPosts(false); // Первая загрузка для нового типа ленты
});

const handlePostCreatedLocally = (newPost) => {
  // Добавляем новый пост в начало списка, если активна лента "Все посты"
  // или если это пост от тренера, на которого мы подписаны (сложнее)
  // Также проверяем, что пост не пришел от другого пользователя, если это лента подписок
  if (activeFeed.value === 'all') {
    posts.value.unshift(newPost);
  } else if (activeFeed.value === 'subscriptions') {
    // Для ленты подписок, если пост создал текущий пользователь (тренер),
    // и он видит свою ленту подписок (где его посты тоже могут быть), то добавляем.
    // Или, если есть более сложная логика проверки подписки на автора нового поста.
    // Самый простой вариант - перезапросить, но для UX лучше добавить сразу.
    // TODO: Уточнить логику для ленты подписок. Пока просто перезагрузим.
    fetchPosts(false);
  }
};

const handlePostDeleted = (deletedPostId) => {
  posts.value = posts.value.filter(p => p.id !== deletedPostId);
  // Можно добавить снекбар
};

const handleFollowStatusChanged = ({ authorId, isFollowing }) => {
  // Эта логика может быть сложной, если нужно обновлять статус во всех постах
  // Если лента "Мои подписки", возможно, потребуется перезагрузка или удаление/добавление постов
  console.log(`HomePage: Author ${authorId} follow status changed to ${isFollowing}`);
  if (activeFeed.value === 'subscriptions') {
    fetchPosts(false); // Простейший способ обновить ленту подписок
  }
};

const handleLikeStatusChanged = ({ postId, isLiked, likesCount }) => {
  const post = posts.value.find(p => p.id === postId);
  if (post) {
    post.is_liked_by_user = isLiked;
    post.likes_count = likesCount;
  }
};

const handleScroll = () => {
  // Отслеживаем скролл всего окна
  const el = document.documentElement;
  // За 300px до конца страницы начинаем загрузку
  const nearBottomOfPage = el.scrollTop + el.clientHeight >= el.scrollHeight - 300; 

  if (nearBottomOfPage && hasNextPage.value && !loadingMore.value) {
    fetchPosts(true);
  }
};

onMounted(() => {
  fetchCurrentUser(); // Сначала получаем данные о пользователе
  fetchPosts(false); 
  window.addEventListener('scroll', handleScroll, true);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll, true);
});
</script>

<style scoped>
.home-page {
  /* padding-bottom: 50px; */ /* Чтобы было видно индикатор загрузки */
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--vt-c-divider-dark-1);
  padding-bottom: 1rem;
  /* Если хотите "липкий" хедер внутри страницы: */
  /* position: sticky; */
  /* top: 0; */ /* Или top: var(--header-height) если есть глобальный хедер */
  /* background-color: var(--color-background-dark); */
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
  margin: 0 auto; /* Центрируем ленту постов */
}
</style>