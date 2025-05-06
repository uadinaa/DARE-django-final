// src/components/Post/PostItem.vue
<template>
  <div class="card bg-dark text-light border-secondary mb-4">
    <img v-if="post.image" :src="post.image" class="card-img-top" :alt="post.title" style="max-height: 450px; object-fit: cover;">
    <div class="card-body">
      <h5 class="card-title text-success">{{ post.title }}</h5>
      <p class="card-text content-preview" style="white-space: pre-wrap;">{{ truncatedContent }}</p>
      </div>
    <div class="card-footer text-muted small">
      <div class="d-flex justify-content-between align-items-center">
        <span>Автор: {{ post.author_username }}</span>
        <span>
          <i class="bi bi-heart-fill text-danger"></i> {{ post.likes_count }}
          <i class="bi bi-chat-dots-fill ms-2"></i> {{ post.comments ? post.comments.length : 0 }}
          </span>
      </div>
      Дата: {{ new Date(post.created_at).toLocaleString() }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
});

// Для предпросмотра контента, если он слишком длинный
const truncatedContent = computed(() => {
  if (props.post.content && props.post.content.length > 200) {
    return props.post.content.substring(0, 200) + '...';
  }
  return props.post.content;
});
</script>

<style scoped>
.card-img-top {
  border-bottom: 1px solid #444;
}
.content-preview {
  min-height: 60px; /* Чтобы карточки без длинного текста не были слишком маленькими */
}
/* Убедитесь, что Bootstrap Icons подключены глобально или здесь */
/* @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css"); */
</style>