// src/layouts/MainLayout.vue
<template>
  <div class="main-layout">
    <AppSidebar />
    <div :class="contentAreaClass"> 
      <main class="main-content-inner">
        <router-view />
      </main>
    </div>
    <aside v-if="shouldDisplayRightSidebar" class="right-sidebar">
      <TopTrainers />
    </aside>
  </div>
</template>

<script setup>
// ... (остальной <script setup> без изменений) ...
import AppSidebar from '@/components/layout/AppSidebar.vue';
import TopTrainers from '@/components/aside/TopTrainer.vue'; // Убедитесь, что имя файла TopTrainer.vue
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const windowWidth = ref(window.innerWidth);
const updateWidth = () => {
  windowWidth.value = window.innerWidth;
};

onMounted(() => {
  window.addEventListener('resize', updateWidth);
});
onUnmounted(() => {
  window.removeEventListener('resize', updateWidth);
});

const showRightSidebarCondition = computed(() => {
  return route.name === 'home';
});

const shouldDisplayRightSidebar = computed(() => {
  return showRightSidebarCondition.value && windowWidth.value > 1200;
});

const contentAreaClass = computed(() => {
  return {
    'main-content-area': true,
    'with-right-sidebar': shouldDisplayRightSidebar.value
  };
});
</script>

<style scoped>
/* ... (секция <style scoped> из предыдущего ответа остается здесь) ... */
.main-layout {
  display: flex;
  width: 100%; 
  flex-grow: 1; 
}

.main-content-area {
  flex-grow: 1; 
  margin-left: var(--sidebar-width); 
  /* background-color: lightcoral; /* Для отладки */
  display: flex; /* Чтобы main-content-inner мог центрироваться, если нужно */
  justify-content: center; /* Центрируем main-content-inner */
  overflow-y: auto; /* Если контент высокий, скролл будет здесь */
  padding-top: var(--default-padding); /* Добавим верхний отступ здесь */
  padding-bottom: var(--default-padding); /* И нижний */
}

/* Динамический отступ для .main-content-area, когда правый сайдбар видим */
.main-content-area.with-right-sidebar {
  margin-right: 300px; /* Ширина правого сайдбара */
}


.main-content-inner {
  /* padding: var(--default-padding); /* Убрали отсюда, перенесли в .main-content-area */
  max-width: 900px; /* <-- ОГРАНИЧИВАЕМ МАКСИМАЛЬНУЮ ШИРИНУ ЦЕНТРАЛЬНОГО КОНТЕНТА */
  width: 100%; /* Чтобы занимал доступную ширину до max-width */
  /* background-color: lightgoldenrodyellow; /* Для отладки */
}

.right-sidebar {
  width: 300px; 
  min-width: 300px;
  height: 100vh; 
  position: fixed; 
  right: 0;
  top: 0;
  padding: var(--default-padding);
  border-left: 1px solid var(--vt-c-divider-dark-2);
  background-color: var(--vt-c-black); 
  overflow-y: auto; 
  z-index: 90; 
}


/* Адаптивность */
@media (max-width: 1200px) {
  .right-sidebar {
    display: none;
  }
  /* Убираем правый отступ у контента, если правый сайдбар скрыт */
  .main-content-area.with-right-sidebar {
    margin-right: 0; 
  }
}

@media (max-width: 768px) {
  .main-content-area {
    margin-left: 0; 
    margin-right: 0; 
    padding-top: 1rem; /* Уменьшаем отступы на мобильных */
    padding-bottom: 1rem;
  }
  .main-content-inner {
    padding: 0 1rem; /* Горизонтальные отступы для внутреннего контента на мобильных */
  }
  /* Логика для мобильного левого сайдбара */
}
</style>