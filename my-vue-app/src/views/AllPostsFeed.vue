// src/views/AllPostsFeed.vue
<template>
  <div class="all-posts-feed container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="text-light">Все посты</h1>
      {/* */}
    </div>

    <div v-if="loading" class="text-center text-light">
      <div class="spinner-border text-success" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p>Загрузка постов...</p>
    </div>

    <div v-if="error" class="alert alert-danger">
      <p>Ошибка при загрузке постов:</p>
      <pre>{{ error.message }}</pre>
      <p v-if="error.response && error.response.data">
        Детали: {{ JSON.stringify(error.response.data) }}
      </p>
    </div>

    <div v-if="!loading && !error && posts.length === 0" class="alert alert-info">
      Пока нет ни одного поста.
    </div>

    <div v-if="!loading && !error && posts.length > 0" class="row">
      <div class="col-md-10 offset-md-1 col-lg-8 offset-lg-2">
        <PostItem v-for="post in posts" :key="post.id" :post="post" />
      </div>
    </div>

    {/* --- КНОПКА ВЫХОДА И ЛОГИКА УДАЛЕНЫ ОТСЮДА --- */}

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import apiClient from '../services/api.js';
import PostItem from '@/components/Post/PostItem.vue';
// import { useRouter } from 'vue-router'; // Больше не нужен здесь для выхода

const posts = ref([]);
const loading = ref(true);
const error = ref(null);
// const router = useRouter(); // Больше не нужен здесь для выхода

// Определяем, вошел ли пользователь (может быть полезно для других фич, например, лайков)
// const isLoggedIn = computed(() => { // Можно удалить, если не используется здесь
//   if (typeof window !== 'undefined' && window.localStorage) {
//       return !!localStorage.getItem('accessToken');
//   }
//   return false;
// });

const fetchPosts = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/posts/');
    posts.value = response.data.results || response.data;
  } catch (err) {
    console.error("Ошибка при загрузке постов:", err);
    error.value = err;
    // Дополнительная проверка на 401 ошибку здесь может быть полезна
    if (err.response && err.response.status === 401 && typeof window !== 'undefined') {
        // Если токен протух или невалиден, возможно, стоит очистить localStorage и перенаправить
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        // router.push({ name: 'login' }); // Понадобится router, если раскомментировать
        window.location.href = '/login'; // Простой редирект
    }
  } finally {
    loading.value = false;
  }
};

// --- ЛОГИКА ВЫХОДА УДАЛЕНА ---
// const performLogout = () => { ... };

onMounted(() => {
  fetchPosts();
});
</script>

<style scoped>
/* Стили для этой страницы */
</style>