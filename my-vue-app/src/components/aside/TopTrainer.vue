// src/components/aside/TopTrainer.vue
<template>
  <div class="top-trainers-widget">
    <h5 class="widget-title">{{ widgetTitle }}</h5>

    <div class="mb-3">
      <input 
        type="text" 
        class="form-control form-control-sm form-control-dark" 
        placeholder="Поиск тренеров по имени..."
        v-model="searchQuery"
      />
    </div>

    <div v-if="loading" class="text-center text-muted small py-3">
      <div class="spinner-border spinner-border-sm" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger_custom small p-2">
      {{ error }}
    </div>

    <ul v-else-if="displayedTrainers.length" class="list-unstyled">
      <li v-for="trainer in displayedTrainers" :key="trainer.id" class="trainer-item mb-3">
        <router-link :to="{ name: 'user-detail', params: { userId: trainer.id } }" class="trainer-link d-flex align-items-center">
          <img 
            :src="trainer.profile?.avatar_url || defaultAvatarUrl" 
            alt="Аватар" 
            class="avatar-sm me-2"
          />
          <div class="trainer-info">
            <span class="trainer-username">{{ trainer.username }}</span>
            <span class="trainer-level d-block small">Уровень: {{ trainer.profile?.level_score || 0 }}</span>
          </div>
        </router-link>
      </li>
    </ul>
    <p v-else class="text-muted small py-3">{{ emptyResultMessage }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import apiClient from '@/services/api';

// --- Состояния (Refs) ---
const topTrainersList = ref([]);      // Список топ-10 тренеров
const allUsersList = ref([]);         // Список всех пользователей для поиска
const searchQuery = ref('');
const isLoading = ref(false);         // Единый флаг загрузки
const error = ref(null);
const defaultAvatarUrl = ref('@/assets/default-avatar.png');
const allUsersEverLoaded = ref(false); // Флаг, что все пользователи были хотя бы раз успешно загружены

// --- Computed Свойства ---

// Активен ли поиск (есть текст в searchQuery)
const isSearchActive = computed(() => searchQuery.value.trim() !== '');

// Заголовок виджета
const widgetTitle = computed(() => isSearchActive.value ? 'Результаты Поиска' : 'Топ Тренеров');

// Фильтрует allUsersList, оставляя только тренеров
const allTrainersFromUsers = computed(() => {
  if (!allUsersEverLoaded.value) return [];
  return allUsersList.value.filter(user => user.profile && user.profile.role === 'trainer');
});

// Результаты поиска (фильтрация allTrainersFromUsers по searchQuery)
const searchResults = computed(() => {
  if (!isSearchActive.value || !allUsersEverLoaded.value) return [];
  const query = searchQuery.value.toLowerCase();
  return allTrainersFromUsers.value.filter(trainer => 
    trainer.username.toLowerCase().includes(query)
  );
});

// Список тренеров, который будет отображаться в шаблоне
const displayedTrainers = computed(() => {
  if (isSearchActive.value) {
    return searchResults.value;
  }
  // Если поиск не активен, показываем топ-10, даже если они еще не загружены (будет пустой список или загрузка)
  return topTrainersList.value;
});

// Сообщение, если список пуст
const emptyResultMessage = computed(() => {
  if (isLoading.value) return ''; // Не показывать сообщение во время загрузки
  if (isSearchActive.value) return 'Тренеры по вашему запросу не найдены.';
  return 'Нет топ тренеров для отображения.';
});


// --- Функции (Methods) ---

// Загрузка топ-10 тренеров
const fetchTopTrainers = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/users/trainers/top/');
    topTrainersList.value = response.data.results || response.data || [];
  } catch (err) {
    console.error("Error fetching top trainers:", err);
    error.value = "Не удалось загрузить топ тренеров.";
    topTrainersList.value = []; // Очищаем в случае ошибки
  } finally {
    // Завершаем загрузку только если не идет параллельная загрузка всех пользователей
    if (!isSearchActive.value || (isSearchActive.value && allUsersEverLoaded.value)) {
        isLoading.value = false;
    }
  }
};

// Загрузка всех пользователей (с пагинацией)
const fetchAllUsers = async () => {
  if (allUsersEverLoaded.value) return; // Не загружать повторно

  isLoading.value = true;
  error.value = null; // Сбрасываем предыдущую ошибку
  let accumulatedUsers = [];
  try {
    let nextPageUrl = '/users/';
    while (nextPageUrl) {
      const response = await apiClient.get(nextPageUrl);
      const usersData = response.data.results || response.data;
      if (Array.isArray(usersData)) {
        accumulatedUsers = accumulatedUsers.concat(usersData);
      }
      nextPageUrl = response.data.next;
    }
    allUsersList.value = accumulatedUsers;
    allUsersEverLoaded.value = true; // Устанавливаем флаг после успешной загрузки
  } catch (err) {
    console.error("Error fetching all users:", err);
    error.value = "Не удалось загрузить список пользователей для поиска.";
    allUsersList.value = []; // Очищаем в случае ошибки
  } finally {
    isLoading.value = false; // Загрузка всех пользователей завершена
  }
};

// --- Watchers and Lifecycle Hooks ---

// Следим за searchQuery
let debounceTimer = null;
watch(searchQuery, (newValue) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(async () => {
    if (newValue.trim() !== '') { // Если поиск активен
      if (!allUsersEverLoaded.value) {
        await fetchAllUsers(); // Загружаем всех пользователей, если еще не загружены
      }
      // Результаты поиска обновятся через computed свойство searchResults
    } else {
      // Поиск очищен. Если топ тренеры пусты, можно их перезагрузить.
      // Обычно displayedTrainers просто переключится на topTrainersList.
      if (topTrainersList.value.length === 0 && !isLoading.value) {
         await fetchTopTrainers();
      }
      error.value = null; // Очищаем ошибку поиска, если она была
    }
  }, 300); // Задержка для дебаунса
});

onMounted(async () => {
  await fetchTopTrainers(); // При монтировании загружаем топ тренеров
});

</script>

<style scoped>
/* Твои стили */
.top-trainers-widget {
  padding: 15px;
  background-color: var(--vt-c-black-mute);
  border-radius: 8px;
}
.widget-title {
  color: var(--vt-c-text-dark-1);
  margin-bottom: 15px;
  border-bottom: 1px solid var(--vt-c-divider-dark-2);
  padding-bottom: 10px;
  font-size: 1.1rem;
}
.trainer-link {
  color: var(--vt-c-text-dark-2);
  text-decoration: none;
  transition: background-color 0.2s ease;
  padding: 8px;
  border-radius: 6px;
  display: flex; 
  align-items: center; 
}
.trainer-link:hover {
  background-color: var(--vt-c-black-soft); 
  color: var(--color-accent); 
}
.avatar-sm {
  width: 40px; 
  height: 40px;
  border-radius: 50%;
  object-fit: cover; 
  border: 1px solid var(--vt-c-divider-dark-1); 
}
.trainer-info {
  display: flex;
  flex-direction: column;
}
.trainer-username {
  font-weight: 500;
}
.trainer-level {
  font-size: 0.85em;
  color: var(--vt-c-white-soft);
}
.alert-danger_custom {
  color: #f8d7da;
  background-color: #4e2227;
  border-color: #f5c6cb;
  font-size: 0.9em;
}
.form-control-dark {
  background-color: #343a40;
  color: var(--color-text-dark-theme);
  border-color: var(--color-border-dark-theme);
}
.form-control-dark::placeholder {
  color: var(--color-text-muted-dark-theme);
}
.form-control-dark:focus {
  background-color: #343a40;
  color: var(--color-text-dark-theme);
  border-color: var(--color-accent);
  box-shadow: 0 0 0 0.2rem var(--color-accent-hover);
}
</style>