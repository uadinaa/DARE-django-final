<template>
  <div
    class="post-item-new mb-4 text-light"
    @click="navigateToPostDetailIfNotInteractive"
    role="article"
    :aria-labelledby="`post-username-${post.id}`"
  >
    <div class="post-header d-flex align-items-center mb-2">
      <router-link
        :to="authorProfileLink"
        class="author-link d-flex align-items-center text-decoration-none"
        @click.stop
      >
        <img :src="post.author?.profile?.avatar_url || defaultAvatar" alt="Аватар" class="author-avatar me-2">
        <div class="author-details">
          <span class="author-username fw-bold text-light" :id="`post-username-${post.id}`">{{ post.author?.username || 'Аноним' }}</span>
          <span v-if="post.author?.profile?.role === 'trainer'" class="author-level d-block small">
            Уровень: {{ post.author?.profile?.level_score || 0 }}
          </span>
        </div>
      </router-link>

      <div class="ms-auto d-flex align-items-center">
        <span class="post-date small me-2">{{ formattedDate }}</span>
        <div class="dropdown post-actions-container" v-if="isCurrentUserAuthor" @click.stop>
          <button
            class="btn btn-sm btn-icon text-light"
            type="button"
            @click.stop="toggleDropdown"
            :aria-expanded="dropdownOpen.toString()"
            title="Действия с постом"
          >
            <i class="bi bi-three-dots-vertical"></i>
          </button>
          <ul :class="['dropdown-menu', 'dropdown-menu-dark', 'dropdown-menu-end', { show: dropdownOpen }]">
            <li>
              <a class="dropdown-item" href="#" @click.prevent="handleEditPost">Редактировать пост</a>
            </li>
            <li>
              <a class="dropdown-item text-danger" href="#" @click.prevent="handleDeletePost">Удалить пост</a>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div class="post-content mb-2" :id="`post-content-preview-${post.id}`">
      <p class="text-light mb-0 post-text-content">
        {{ displayContent }}
      </p>
    </div>

    <img v-if="post.image && !isDetailedView" :src="post.image" class="post-image w-100" alt="Изображение поста">

    <div class="post-metrics d-flex justify-content-end align-items-center mt-2">
      <button @click.stop="toggleLike" class="btn btn-sm border-0 p-0 me-3 like-button" :class="{'liked': isLikedByCurrentUser}">
        <i :class="isLikedByCurrentUser ? 'bi bi-heart-fill' : 'bi bi-heart'"></i>
        <span class="ms-1 metric-count">{{ localLikesCount }}</span>
      </button>
      <router-link :to="{ name: 'post-detail', params: { id: post.id } }" class="text-decoration-none comment-link" @click.stop>
        <i class="bi bi-chat-dots-fill"></i>
        <span class="ms-1 metric-count">{{ localCommentsCount }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';
import { formatPostDate } from '@/utils/dateFormatter';

const props = defineProps({
  post: {
    type: Object,
    required: true
  },
  isDetailedView: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits([
  'post-deleted',
  'like-status-changed',
]);

const router = useRouter();

const currentUserId = ref(null);
const isLoggedIn = ref(false);

const loadAuthDataFromLocalStorage = () => {
  const token = localStorage.getItem('accessToken');
  isLoggedIn.value = !!token;
  if (token) {
    try {
      const storedUserId = localStorage.getItem('currentUserId');
      currentUserId.value = storedUserId ? parseInt(storedUserId, 10) : null;
    } catch (e) {
      console.error("Error reading auth data from localStorage:", e);
      isLoggedIn.value = false;
      currentUserId.value = null;
    }
  } else {
    currentUserId.value = null;
  }
};

loadAuthDataFromLocalStorage();

const defaultAvatar = '/src/assets/default-avatar.png';
const dropdownOpen = ref(false);

const localLikesCount = ref(0);
const isLikedByCurrentUser = ref(false);
const localCommentsCount = ref(0);

const authorProfileLink = computed(() => {
  if (!props.post.author || !props.post.author.id) return { name: 'home' };
  return { name: 'user-detail', params: { userId: props.post.author.id } };
});

// Новое вычисляемое свойство для определения, является ли текущий пользователь автором поста
const isCurrentUserAuthor = computed(() => {
  return isLoggedIn.value && props.post.author && currentUserId.value === props.post.author.id;
});

const canEdit = computed(() => {
  return isCurrentUserAuthor.value; // Редактировать может автор
});

const canDelete = computed(() => {

  const isAdmin = localStorage.getItem('currentUserRole') === 'admin' || localStorage.getItem('currentUserIsStaff') === 'true';
  return isLoggedIn.value && props.post.author &&
         (currentUserId.value === props.post.author.id || isAdmin);
});


watch(() => props.post, (newPost) => {
  localLikesCount.value = newPost.likes_count || 0;
  isLikedByCurrentUser.value = newPost.is_liked_by_user || false;
  localCommentsCount.value = newPost.comments_count || 0;
}, { immediate: true, deep: true });

const formattedDate = computed(() => {
  if (!props.post.created_at) return '';
  return formatPostDate(props.post.created_at);
});

const displayContent = computed(() => {
  let content = props.post.content || '';
  if (!props.isDetailedView && content.length > 250) {
    content = content.substring(0, 250) + '...';
  }
  return content.trim();
});

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value;
};

const handleEditPost = () => {
  console.log('Edit post:', props.post.id);
  // TODO: router.push({ name: 'post-edit', params: { id: props.post.id } });
  dropdownOpen.value = false;
};

const handleDeletePost = async () => {
  if (!isCurrentUserAuthor.value && !currentUserRoleIsAdminOrModerator.value) { // Упрощенная проверка для этого UI
      console.warn("Delete attempt by non-authorized user prevented by UI logic.");
      dropdownOpen.value = false;
      return;
  }

  if (window.confirm('Вы уверены, что хотите удалить этот пост?')) {
    try {
      await apiClient.delete(`/posts/${props.post.id}/`);
      emit('post-deleted', props.post.id);
    } catch (error) {
      console.error('Error deleting post:', error);
    }
  }
  dropdownOpen.value = false;
};

const toggleLike = async () => {
  if (!isLoggedIn.value) {
    router.push({ name: 'login' });
    return;
  }
  const newIsLiked = !isLikedByCurrentUser.value;
  const newLikesCount = newIsLiked ? localLikesCount.value + 1 : localLikesCount.value - 1;

  isLikedByCurrentUser.value = newIsLiked;
  localLikesCount.value = newLikesCount;

  const action = newIsLiked ? 'POST' : 'DELETE';
  try {
    await apiClient({
      method: action,
      url: `/posts/${props.post.id}/like/`
    });
    emit('like-status-changed', {
        postId: props.post.id,
        isLiked: isLikedByCurrentUser.value,
        likesCount: localLikesCount.value
    });
  } catch (error) {
    console.error('Error toggling like:', error);
    isLikedByCurrentUser.value = !newIsLiked; // Откатываем
    localLikesCount.value = newIsLiked ? newLikesCount - 1 : newLikesCount + 1; // Откатываем
    // TODO: Показать снекбар с ошибкой
  }
};

const closeDropdownOnClickOutside = (event) => {
  if (dropdownOpen.value && !event.target.closest('.post-actions-container')) {
    dropdownOpen.value = false;
  }
};

const navigateToPostDetailIfNotInteractive = (event) => {
  if (props.isDetailedView) return;
  if (event.target.closest('button, a, .dropdown-menu')) {
    return;
  }
  router.push({ name: 'post-detail', params: { id: props.post.id } });
};

onMounted(() => {
  // loadAuthDataFromLocalStorage(); // Уже вызван
  document.addEventListener('click', closeDropdownOnClickOutside);
});
onUnmounted(() => {
  document.removeEventListener('click', closeDropdownOnClickOutside);
});

</script>

<style scoped>
/* Стили остаются такими же, как в вашем предыдущем полном примере PostItem.vue */
.post-item-new {
  background-color: var(--color-card-bg-dark);
  border: 1px solid var(--vt-c-divider-dark-2);
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
}

.post-header {}
.author-link {}
.author-avatar { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }
.author-details { display: flex; flex-direction: column; justify-content: center; }
.author-username { font-size: 0.95rem; line-height: 1.2; }
.author-level { font-size: 0.75rem; color: var(--vt-c-white-soft); line-height: 1.2; }
.post-date { font-size: 0.75rem; color: var(--vt-c-text-dark-2);}
.post-actions-container { position: relative; }
.btn-icon { padding: 0.25rem 0.5rem; line-height: 1; }
.dropdown-menu { min-width: 180px; } /* Уменьшим, если "Подписаться" было самым длинным */
.dropdown-menu.show { display: block; z-index: 1056; }
.dropdown-item { font-size: 0.9rem; }
.dropdown-item.text-danger:hover { background-color: #a71d2a; color: white !important; }

.post-content {}
.post-text-content {
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: var(--vt-c-text-dark-1);
  cursor: pointer; 
}

.post-image {
  width: 100%;
  max-height: 500px;
  object-fit: cover;
  border-radius: 8px;
  display: block;
  margin-top: 0.75rem;
  margin-bottom: 0.75rem;
  cursor: pointer; 
}

.post-metrics {}
.post-metrics .btn,
.post-metrics .comment-link {
  color: var(--vt-c-text-dark-1);
  font-size: 0.85rem;
  text-decoration: none;
}
.post-metrics .btn:hover,
.post-metrics .comment-link:hover {
  color: var(--vt-c-white);
}
.post-metrics .like-button.liked i,
.post-metrics .like-button .bi-heart-fill {
  color: var(--bs-danger) !important;
}
.post-metrics .like-button .bi-heart {
   color: var(--vt-c-text-dark-1);
}
.post-metrics .like-button:hover i,
.post-metrics .comment-link:hover i {
  transform: scale(1.1);
}
.post-metrics .metric-count {
   color: var(--vt-c-text-dark-1);
   margin-left: 0.25rem;
}
</style>