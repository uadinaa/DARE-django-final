<template>
    <div class="comment-item d-flex mb-3">
      <img :src="comment.author?.profile?.avatar_url || defaultAvatar" alt="Аватар" class="author-avatar me-2 mt-1">
      <div class="comment-body bg-dark-lighter p-2 rounded flex-grow-1">
        <div class="comment-header d-flex justify-content-between align-items-center mb-1">
          <span class="author-username fw-bold text-light">{{ comment.author?.username || 'Аноним' }}</span>
          <div class="d-flex align-items-center">
            <span class="comment-date text-muted small me-2">{{ formattedCommentDate }}</span>
            <div class="dropdown comment-actions-container" v-if="isCurrentUserCommentAuthor" @click.stop>
              <button class="btn btn-sm btn-icon text-light p-0" type="button" @click.stop="toggleDropdown">
                <i class="bi bi-three-dots-vertical small"></i>
              </button>
              <ul :class="['dropdown-menu', 'dropdown-menu-dark', 'dropdown-menu-end', { show: dropdownOpen }]">
                <li><a class="dropdown-item text-danger" href="#" @click.prevent="deleteComment">Удалить</a></li>
              </ul>
            </div>
          </div>
        </div>
        <p class="comment-text text-light small mb-0" style="white-space: pre-wrap;">{{ comment.content }}</p>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, onUnmounted } from 'vue';
  import { formatPostDate } from '@/utils/dateFormatter'; // Используем ту же функцию, что и для постов в ленте
  
  const props = defineProps({
    comment: {
      type: Object,
      required: true
    }
  });
  
  const emit = defineEmits(['comment-deleted']);
  
  // ЗАГЛУШКА - ЗАМЕНИТЕ НА ДАННЫЕ ИЗ ВАШЕГО STORE
  const currentUserId = ref(localStorage.getItem('currentUserId') ? parseInt(localStorage.getItem('currentUserId'), 10) : null);
  // -----------------------------------------------
  
  const defaultAvatar = '/src/assets/default-avatar.png';
  const dropdownOpen = ref(false);
  
  const formattedCommentDate = computed(() => {
    if (!props.comment.created_at) return '';
    return formatPostDate(props.comment.created_at); // Используем общий форматер для ленты
  });
  
  const isCurrentUserCommentAuthor = computed(() => {
    return currentUserId.value && props.comment.author && currentUserId.value === props.comment.author.id;
  });
  
  const toggleDropdown = () => {
    dropdownOpen.value = !dropdownOpen.value;
  };
  
  const deleteComment = () => {
    if (!isCurrentUserCommentAuthor.value) return;
    if (window.confirm('Вы уверены, что хотите удалить этот комментарий?')) {
      // TODO: apiClient.delete(`/posts/${props.comment.post}/comments/${props.comment.id}/`)
      // затем emit('comment-deleted', props.comment.id);
      console.log('Deleting comment', props.comment.id, 'for post', props.comment.post);
      dropdownOpen.value = false;
      emit('comment-deleted', props.comment.id); // Оптимистичное удаление для примера
    }
  };
  
  const closeDropdownOnClickOutside = (event) => {
    if (dropdownOpen.value && !event.target.closest('.comment-actions-container')) {
      dropdownOpen.value = false;
    }
  };
  
  onMounted(() => {
    document.addEventListener('click', closeDropdownOnClickOutside);
  });
  onUnmounted(() => {
    document.removeEventListener('click', closeDropdownOnClickOutside);
  });
  </script>
  
  <style scoped>
  .comment-item {
    font-size: 0.9rem;
  }
  .author-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
  }
  .bg-dark-lighter {
    background-color: var(--vt-c-black-mute); /* Пример фона для комментария */
  }
  .author-username {
    font-size: 0.85rem;
  }
  .comment-date {
    font-size: 0.75rem;
  }
  .comment-text {
    line-height: 1.5;
  }
  .comment-actions-container .btn-icon i {
    font-size: 0.8rem; /* Меньше иконка троеточия */
  }
  .dropdown-menu {
    min-width: 120px; /* Меню поменьше */
  }
  </style>