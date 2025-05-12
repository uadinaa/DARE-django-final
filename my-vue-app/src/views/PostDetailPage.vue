<template>
  <div class="post-detail-page container py-3">
    <div v-if="loading" class="text-center text-light mt-5">
      <div class="spinner-border text-success" role="status"></div>
      <p>Загрузка поста...</p>
    </div>
    <div v-else-if="error" class="alert alert-danger">
      Ошибка: {{ error.message }}
      <span v-if="error.response && error.response.status === 404">Пост не найден.</span>
    </div>
    <div v-else-if="postData" class="post-content-area">
      <PostItem :post="postData" :is-detailed-view="true" 
        @post-deleted="handlePostDeleted"
        @follow-status-changed="handleFollowChangeInDetail"
        @like-status-changed="handleLikeChangeInDetail"
      />

      <hr class="border-secondary">

      <div class="add-comment-form mt-4 mb-4" v-if="isLoggedIn">
        <h5 class="text-light mb-2">Оставить комментарий:</h5>
        <form @submit.prevent="submitComment">
          <textarea 
            v-model="newCommentText" 
            class="form-control form-control-dark mb-2" 
            rows="3" 
            placeholder="Ваш комментарий..."
            required
          ></textarea>
          <button type="submit" class="btn btn-success btn-sm" :disabled="commentSubmitting">
            {{ commentSubmitting ? 'Отправка...' : 'Отправить' }}
          </button>
          <div v-if="commentError" class="alert alert-danger_custom small mt-2 p-2">{{ commentError }}</div>
        </form>
      </div>

      <div class="comments-section mt-4">
        <h4 class="text-success mb-3">Комментарии ({{ comments.length }})</h4>
        <div v-if="loadingComments" class="text-center text-light small"><div class="spinner-border spinner-border-sm"></div> Загрузка...</div>
        <div v-else-if="commentsError" class="alert alert-warning small">Не удалось загрузить комментарии.</div>
        <div v-else-if="comments.length > 0" class="comments-list">
          <CommentItem 
            v-for="comment in comments" 
            :key="comment.id" 
            :comment="comment"
            @comment-deleted="handleCommentDeletedInList"
          />
          </div>
        <p v-else class="text-muted small">Комментариев пока нет.</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import PostItem from '@/components/Post/PostItem.vue'; // Ваш основной компонент поста
import CommentItem from '@/components/Comment/CommentItem.vue'; // Новый компонент комментария
import { formatPostDetailDate } from '@/utils/dateFormatter'; // Новая функция форматирования

const props = defineProps({
  id: { type: [String, Number], required: true } // post_id из маршрута
});

const router = useRouter();
const postData = ref(null);
const loading = ref(true);
const error = ref(null);

const comments = ref([]);
const loadingComments = ref(false);
const commentsError = ref(null);

const newCommentText = ref('');
const commentSubmitting = ref(false);
const commentError = ref('');

// ЗАГЛУШКА - ЗАМЕНИТЕ НА ДАННЫE ИЗ ВАШЕГО STORE
const isLoggedIn = ref(!!localStorage.getItem('accessToken'));
// -----------------------------------------------

const formattedPostDetailDate = computed(() => {
  if (!postData.value?.created_at) return '';
  return formatPostDetailDate(postData.value.created_at);
});

const fetchPostDetails = async (postId) => {
  if (!postId) return;
  loading.value = true; error.value = null; postData.value = null;
  try {
    const response = await apiClient.get(`/posts/${postId}/`);
    postData.value = response.data;
    await fetchComments(postId); // Загружаем комментарии после загрузки поста
  } catch (err) {
    console.error('Error fetching post details:', err);
    error.value = err;
  } finally {
    loading.value = false;
  }
};

const fetchComments = async (postId) => {
  if (!postId) return;
  loadingComments.value = true; commentsError.value = null;
  try {
    const response = await apiClient.get(`/posts/${postId}/comments/`);
    // Бэкенд должен сортировать от новых к старым
    comments.value = response.data.results || response.data || []; 
  } catch (err) {
    console.error('Error fetching comments:', err);
    commentsError.value = err;
  } finally {
    loadingComments.value = false;
  }
};

const submitComment = async () => {
  if (!newCommentText.value.trim() || !postData.value) return;
  commentSubmitting.value = true;
  commentError.value = '';
  try {
    const response = await apiClient.post(`/posts/${postData.value.id}/comments/`, {
      content: newCommentText.value
    });
    comments.value.unshift(response.data); // Добавляем новый коммент в начало списка (оптимистично)
    newCommentText.value = ''; // Очищаем поле ввода
    // Обновляем счетчик комментариев в postData для немедленного отображения
    if (postData.value) {
        postData.value.comments_count = (postData.value.comments_count || 0) + 1;
    }
  } catch (err) {
    console.error('Error submitting comment:', err);
    commentError.value = 'Не удалось отправить комментарий.';
  } finally {
    commentSubmitting.value = false;
  }
};

// Обработчики событий от PostItem
const handlePostDeleted = (deletedPostId) => {
  console.log('Post deleted event received in detail page, id:', deletedPostId);
  // Если текущий пост удален, перенаправляем на главную
  if (postData.value && postData.value.id === deletedPostId) {
    router.push({ name: 'home' });
    // TODO: Показать снекбар "Пост удален"
  }
};

const handleFollowChangeInDetail = ({ authorId, isFollowing }) => {
  // Эта функция вызывается, если пользователь кликнул "подписаться" на автора
  // из меню троеточия на детальной странице.
  // Здесь можно обновить состояние подписки, если оно где-то глобально хранится,
  // или если на детальной странице профиля автора есть кнопка подписки.
  // Для самого PostItem это вряд ли что-то изменит визуально.
  console.log(`Follow status for author ${authorId} changed to ${isFollowing} from detail view.`);
};

const handleLikeChangeInDetail = ({ postId, isLiked, likesCount }) => {
  if (postData.value && postData.value.id === postId) {
    postData.value.is_liked_by_user = isLiked;
    postData.value.likes_count = likesCount;
  }
};

const handleCommentDeletedInList = (deletedCommentId) => {
    comments.value = comments.value.filter(c => c.id !== deletedCommentId);
    if (postData.value && postData.value.comments_count > 0) {
        postData.value.comments_count--;
    }
};


onMounted(() => {
  fetchPostDetails(props.id);
});

watch(() => props.id, (newId) => {
  if (newId) {
    fetchPostDetails(newId);
  }
});

</script>

<style scoped>
.post-detail-page {
  color: var(--vt-c-text-dark-1);
  max-width: 800px; /* Ограничим ширину для лучшей читаемости */
  margin: 0 auto;
}
.post-content-area {
  /* Сюда можно добавить фон, если нужно отделить от общего фона страницы */
  background-color: var(--color-card-bg-dark); /* Используем фон как у карточки */
  padding: 1rem; /* Убрали из PostItem, добавляем здесь */
  border-radius: 8px;
  border: 1px solid var(--vt-c-divider-dark-2);
}

.post-meta-footer {
  /* background-color: var(--vt-c-black-soft); */
  /* padding: 0.5rem 1rem; */
  /* border-top: 1px solid var(--vt-c-divider-dark-1); */
}
.detailed-post-date {
  /* стили для даты */
}
.post-metrics-detailed {
  /* стили для блока метрик */
}
.post-metrics-detailed span {
  color: var(--vt-c-text-dark-1);
}
.post-metrics-detailed i {
  margin-right: 0.25rem;
}
.post-metrics-detailed .text-danger i {
    color: var(--bs-danger) !important;
}


.add-comment-form {
  /* Стили для формы добавления комментария */
}
.comments-section {
  /* Стили для секции комментариев */
}
.comments-list {
  max-height: 500px; /* Пример ограничения высоты для скролла */
  overflow-y: auto;
  padding-right: 10px; /* Для полосы прокрутки, чтобы не наезжала на контент */
}
.alert-danger_custom {
  color: #f8d7da;
  background-color: #4e2227;
  border-color: #f5c6cb;
}
</style>