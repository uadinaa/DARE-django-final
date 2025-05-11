<template>
    <div class="post-detail-page">
      <h1>Детали Поста</h1>
      <p>Здесь будет отображаться подробная информация о посте (ID: {{ postId }}) и его комментарии.</p>
      <div v-if="post">
        <h2>{{ post.author?.username }}: {{ post.content?.substring(0, 50) }}...</h2>
        <p>{{ post.content }}</p>
        <img v-if="post.image" :src="post.image" alt="Post Image" style="max-width: 300px;">
        </div>
      <div v-else>
        <p>Загрузка данных поста...</p>
      </div>
  
      <hr>
      <h3>Комментарии</h3>
      </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue';
  import { useRoute } from 'vue-router';
  // import apiClient from '@/services/api'; // Раскомментируйте для API запросов
  
  const route = useRoute();
  const postId = computed(() => route.params.id); // Получаем ID из маршрута
  const post = ref(null); // Здесь будут данные поста
  // const comments = ref([]); // Здесь будут комментарии
  
  // Пример загрузки данных (нужно раскомментировать и доработать)
  /*
  onMounted(async () => {
    if (postId.value) {
      try {
        // console.log(`Workspaceing post with ID: ${postId.value}`);
        // const response = await apiClient.get(`/posts/${postId.value}/`);
        // post.value = response.data;
        // console.log('Post data:', post.value);
        // TODO: Fetch comments
      } catch (error) {
        console.error('Error fetching post details:', error);
      }
    }
  });
  */
  </script>
  
  <style scoped>
  .post-detail-page {
    padding: 20px;
  }
  img {
    margin-top: 10px;
    display: block;
  }
  </style>