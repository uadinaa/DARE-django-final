<template>
  <div class="auth-layout">
    <AppHeader />
    <main class="auth-content fullscreen-center"> <router-view />
    </main>
  </div>
</template>

<script setup>
import AppHeader from '@/components/layout/AppHeader.vue';
</script>

<style scoped>
.auth-layout {
  display: flex;
  flex-direction: column;
  width: 100%; /* Занимает всю ширину #app */
  flex-grow: 1;
}
.auth-content {
  /* Стили для .fullscreen-center уже применены */
}
</style>