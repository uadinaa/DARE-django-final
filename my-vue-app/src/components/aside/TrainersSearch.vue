<template>
  <div class="trainers-search-sidebar p-3 bg-dark-lighter rounded">
    <h5 class="text-light mb-3">Поиск Тренеров</h5> 
    
    <div class="mb-3">
      <input 
        type="text" 
        class="form-control form-control-sm form-control-dark" 
        placeholder="Введите имя тренера..."
        v-model="searchQuery"
      />
    </div>

    <div v-if="isLoading" class="text-center text-light">
      <div class="spinner-border spinner-border-sm" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    
    <ul v-else-if="filteredTrainers.length > 0" class="list-unstyled">
      <li v-for="trainer in filteredTrainers" :key="trainer.id" class="mb-2">
        <router-link :to="{ name: 'user-detail', params: { userId: trainer.id } }" class="d-flex align-items-center text-decoration-none text-light trainer-link">
          <img :src="trainer.profile?.avatar_url || defaultAvatar" alt="avatar" class="rounded-circle me-2" width="30" height="30">
          <div>
            <small>{{ trainer.username }}</small>
            <div class="trainer-level">Уровень: {{ trainer.profile?.level_score || 0 }}</div>
          </div>
        </router-link>
      </li>
    </ul>
    <div v-else-if="searchQuery && !isLoading" class="text-light"><small>Тренеры не найдены.</small></div>
    <div v-else-if="!isLoading && !searchQuery && allUsersLoaded" class="text-light"><small>Введите имя для поиска тренера.</small></div>
    <div v-else-if="!isLoading && !allUsersLoaded && !error" class="text-light"><small>Загрузка списка пользователей...</small></div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api'; 
import defaultAvatar from '@/assets/default-avatar-icon.jpg'; // Убедись, что путь верный

const allUsers = ref([]); // Хранилище для всех загруженных пользователей
const isLoading = ref(false);
const error = ref(null);
const searchQuery = ref('');
const allUsersLoaded = ref(false); // Флаг, что все пользователи загружены

const fetchAllUsers = async () => {
  isLoading.value = true;
  allUsersLoaded.value = false;
  error.value = null;
  let fetchedUsersAccumulator = []; // Временный массив для накопления пользователей
  try {
    let nextPageUrl = '/users/'; // Начальный URL для UserViewSet

    while (nextPageUrl) {
      const response = await apiClient.get(nextPageUrl);
      if (response.data && response.data.results) {
        fetchedUsersAccumulator = fetchedUsersAccumulator.concat(response.data.results);
      } else if (response.data && Array.isArray(response.data)) { 
        // Если API вернул просто массив (без пагинации или это последняя страница без 'results')
        fetchedUsersAccumulator = fetchedUsersAccumulator.concat(response.data);
      }
      nextPageUrl = response.data.next; // URL следующей страницы или null
    }
    allUsers.value = fetchedUsersAccumulator;
    allUsersLoaded.value = true; // Устанавливаем флаг после успешной загрузки
    
  } catch (e) {
    console.error("Ошибка при загрузке всех пользователей:", e);
    error.value = 'Не удалось загрузить список пользователей.';
    if (e.response && e.response.data && typeof e.response.data.detail === 'string') {
        error.value = e.response.data.detail;
    }
  } finally {
    isLoading.value = false;
  }
};

// Вычисляемое свойство для получения только тренеров
const trainersList = computed(() => {
  if (!allUsersLoaded.value) return []; // Не фильтровать, пока все не загружено
  return allUsers.value.filter(user => user.profile && user.profile.role === 'trainer');
});

// Вычисляемое свойство для фильтрации тренеров по searchQuery
const filteredTrainers = computed(() => {
  if (!searchQuery.value) {
    // Если поиск пуст, можно показывать топ-N тренеров из trainersList (уже отфильтрованных по роли)
    // Например, топ 7 по уровню
    return trainersList.value
        .slice() // Создаем копию, чтобы не мутировать исходный trainersList
        .sort((a, b) => (b.profile?.level_score || 0) - (a.profile?.level_score || 0))
        .slice(0, 7); // Показываем первых 7 или сколько нужно
  }
  const query = searchQuery.value.toLowerCase();
  return trainersList.value.filter(trainer => 
    trainer.username.toLowerCase().includes(query)
    // Можно добавить и другие поля для поиска, если они есть в `trainer` объекте:
    // || (trainer.first_name && trainer.first_name.toLowerCase().includes(query))
    // || (trainer.last_name && trainer.last_name.toLowerCase().includes(query))
  );
});

onMounted(fetchAllUsers);

</script>

<style scoped>
.trainers-search-sidebar {
  background-color: var(--vt-c-black-mute); /* Пример */
  border-radius: 8px;
}
.trainer-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
.trainer-level {
  font-size: 0.75rem;
  color: var(--color-text-muted-dark-theme);
}
.form-control-sm {
  font-size: 0.8rem;
}
 .bg-dark-lighter { 
    background-color: var(--vt-c-black-soft); 
}
</style>