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
const topTrainersList = ref([]);      // Для топ-10 тренеров
const searchResultsList = ref([]);    // Для результатов поиска со своего эндпоинта
const searchQuery = ref('');
const isLoading = ref(false);
const error = ref(null);
const defaultAvatarUrl = ref('@/assets/default-avatar.png');

// Флаг, чтобы понимать, что сейчас отображаются результаты поиска (даже если они пустые)
const activelySearching = ref(false);


// --- Computed Свойства ---

const widgetTitle = computed(() => activelySearching.value ? 'Результаты Поиска' : 'Топ Тренеров');

const displayedTrainers = computed(() => {
  return activelySearching.value ? searchResultsList.value : topTrainersList.value;
});

const emptyResultMessage = computed(() => {
  if (isLoading.value) return '';
  if (activelySearching.value && searchResultsList.value.length === 0) return 'Тренеры по вашему запросу не найдены.';
  if (!activelySearching.value && topTrainersList.value.length === 0) return 'Нет топ тренеров для отображения.';
  return ''; // Если есть данные, сообщение не нужно
});

// --- Функции (Methods) ---

const fetchTopTrainers = async () => {
  if (isLoading.value && !activelySearching.value) return; // Предотвращаем двойной вызов, если уже грузим топ
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/users/trainers/top/');
    topTrainersList.value = response.data.results || response.data || [];
  } catch (err) {
    console.error("Error fetching top trainers:", err);
    error.value = "Не удалось загрузить топ тренеров.";
    topTrainersList.value = [];
  } finally {
    // Завершаем общую загрузку, только если не выполняется активный поиск
     if (!activelySearching.value) {
       isLoading.value = false;
     }
  }
};

// Функция для поиска тренеров через новый эндпоинт
const searchAllTrainers = async () => {
  if (!searchQuery.value.trim()) { // Если поиск пустой, не делаем запрос
    searchResultsList.value = []; // Очищаем результаты поиска
    activelySearching.value = false; // Выключаем режим активного поиска
    // Если topTrainersList пуст, можно их загрузить
    if (topTrainersList.value.length === 0 && !isLoading.value) {
        await fetchTopTrainers();
    }
    return;
  }

  activelySearching.value = true; // Включаем режим активного поиска
  isLoading.value = true;
  error.value = null;
  searchResultsList.value = []; // Очищаем предыдущие результаты на время запроса
  try {
    // Используем новый эндпоинт /api/users/trainers/all/ с параметром search
    // Пагинация будет обрабатываться на бэкенде, если тренеров много.
    // Фронтенд получит первую страницу результатов. Если нужна загрузка всех страниц поиска - логика усложнится.
    // Пока предполагаем, что первая страница результатов поиска достаточна, или API отдает всех найденных.
    const response = await apiClient.get('/users/trainers/all/', {
      params: {
        search: searchQuery.value.trim()
      }
    });
    searchResultsList.value = response.data.results || response.data || [];
  } catch (err) {
    console.error("Error searching trainers:", err);
    error.value = "Ошибка при поиске тренеров.";
    searchResultsList.value = [];
  } finally {
    isLoading.value = false;
  }
};

// --- Watchers and Lifecycle Hooks ---
let debounceTimer = null;
watch(searchQuery, (newValue) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    if (newValue.trim() !== '') {
      searchAllTrainers();
    } else {
      // Поиск очищен, возвращаемся к топ тренерам
      activelySearching.value = false;
      searchResultsList.value = []; // Очищаем результаты
      error.value = null; // Очищаем ошибку от поиска
      // Проверяем, нужно ли перезагрузить топ-тренеров (если их список пуст)
      if (topTrainersList.value.length === 0 && !isLoading.value) {
          fetchTopTrainers();
      }
    }
  }, 500); // Дебаунс 500 мс
});

onMounted(async () => {
  await fetchTopTrainers(); // При монтировании загружаем только топ тренеров
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