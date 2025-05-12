// src/views/FollowingListPage.vue (Пример, адаптируйте для других списков)
<template>
  <div class="follow-list-page container py-4" ref="scrollComponent">
    <h1 class="text-light mb-4">Подписки {{ targetUsername || 'пользователя' }}</h1>
    <div v-if="initialLoading && listItems.length === 0" class="text-center text-light mt-5">
      <div class="spinner-border text-success" role="status"></div> Загрузка...
    </div>
    <div v-else-if="pageError" class="alert alert-danger">Ошибка: {{ pageError.message }}</div>
    <div v-else-if="listItems.length">
      <ul class="list-group">
        <li v-for="follow in listItems" :key="follow.id" class="list-group-item ...">
          <router-link :to="{ name: 'user-detail', params: { userId: follow.followed.id } }" class="d-flex align-items-center text-decoration-none text-light flex-grow-1">
            <img :src="follow.followed.profile?.avatar_url || defaultAvatar" alt="Аватар" class="avatar-xs me-3 rounded-circle">
            <span>{{ follow.followed.username }}</span>
          </router-link>
        </li>
      </ul>
      <div v-if="loadingMore" class="text-center text-light py-3">
        <div class="spinner-border spinner-border-sm text-success" role="status"></div>
        <p class="mb-0 small">Подгружаем еще...</p>
      </div>
       <div v-if="!hasNextPage && listItems.length > 0 && !initialLoading && !loadingMore" class="text-center text-muted small py-3">
        Больше ни на кого не подписан.
      </div>
    </div>
    <p v-else-if="!initialLoading" class="text-light">Этот пользователь ни на кого не подписан.</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'; // Добавили nextTick
import apiClient from '@/services/api';

const props = defineProps({
  userId: { type: [String, Number], required: true }
});

const listItems = ref([]);
const initialLoading = ref(true);
const loadingMore = ref(false);
const pageError = ref(null);
const targetUsername = ref('');
const defaultAvatar = '/src/assets/default-avatar.png';
const nextPageUrl = ref(null);
const scrollComponent = ref(null); // ref для корневого элемента компонента

const hasNextPage = computed(() => nextPageUrl.value !== null);

// Функция для проверки, нужно ли загружать еще данные
const checkAndLoadMore = async () => {
  // Даем Vue время обновить DOM после добавления новых элементов
  await nextTick(); 

  const element = scrollComponent.value; // Теперь это корневой div компонента
  if (!element) return;

  // Проверяем, есть ли вообще скроллбар или контент полностью помещается
  // (scrollHeight примерно равен clientHeight)
  const contentFitsScreen = element.scrollHeight <= element.clientHeight + 5; // +5 для небольшой погрешности

  // console.log(`checkAndLoadMore: scrollHeight=${element.scrollHeight}, clientHeight=${element.clientHeight}, contentFitsScreen=${contentFitsScreen}, hasNextPage=${hasNextPage.value}, loadingMore=${loadingMore.value}`);

  if (contentFitsScreen && hasNextPage.value && !loadingMore.value) {
    // console.log("Content fits screen, but more pages exist. Fetching more...");
    await fetchList(true); // Рекурсивно вызываем, если нужно загрузить еще
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
    endpoint = `/interactions/users/${props.userId}/following/`;
    // (Загрузка имени пользователя)
    if (!targetUsername.value && props.userId) { // Загружаем имя только один раз
        try {
            const userRes = await apiClient.get(`/users/${props.userId}/`);
            targetUsername.value = userRes.data.username;
        } catch (e) { console.warn("Could not fetch target username", e)}
    }
  }
  pageError.value = null;

  try {
    const response = await apiClient.get(endpoint);
    const results = response.data.results || []; // Убедимся, что results это массив

    if (isLoadMore) {
      listItems.value.push(...results);
    } else {
      listItems.value = results;
    }
    nextPageUrl.value = response.data.next || null;

    // После обновления данных, проверяем, не нужно ли загрузить еще
    await checkAndLoadMore();

  } catch (err) {
    console.error('Error fetching following list:', err);
    pageError.value = err;
  } finally {
    if (isLoadMore) loadingMore.value = false;
    else initialLoading.value = false;
  }
};

const handleScroll = () => {
  const element = scrollComponent.value;
  if (element) {
    // Условие срабатывания подгрузки (например, за 200px до конца)
    const nearBottom = element.scrollTop + element.clientHeight >= element.scrollHeight - 200;
    if (nearBottom && hasNextPage.value && !loadingMore.value) {
      fetchList(true);
    }
  }
};

onMounted(() => {
  if (props.userId) {
    fetchList(false);
  }
  // Привязываем слушатель скролла к самому элементу компонента, если он скроллируемый,
  // или к window, если скроллится вся страница.
  // Если .follow-list-page сам по себе не имеет overflow: auto и фиксированной высоты,
  // то скроллится будет window.
  const scrollTarget = scrollComponent.value; // Или window
  if (scrollTarget) {
    scrollTarget.addEventListener('scroll', handleScroll);
  } else {
    window.addEventListener('scroll', handleScroll, true); // Фоллбек на window
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
    targetUsername.value = ''; // Сбрасываем имя пользователя, чтобы оно загрузилось для нового ID
    fetchList(false);
  }
});
</script>

<style scoped>
.follow-list-page {
  color: var(--vt-c-text-dark-1);
  /* Если вы хотите, чтобы этот блок был скроллируемым, а не вся страница: */
  /* height: calc(100vh - ВЫСОТА_ШАПКИ_И_ДРУГИХ_ЭЛЕМЕНТОВ_НАД_СПИСКОМ); */
  /* overflow-y: auto; */
}
.avatar-xs { width: 40px; height: 40px; object-fit: cover; border: 1px solid var(--vt-c-divider-dark-1); }
.list-group-item a:hover span { color: var(--color-accent); }
.list-group-item { transition: background-color 0.2s ease-in-out; }
.list-group-item:hover { background-color: var(--vt-c-black-soft) !important; }
</style>