<template>
  <component :is="layoutComponent">
    <router-view />
  </component>
</template>

<script setup>
import { computed, shallowRef, watch } from 'vue';
import { useRoute } from 'vue-router';
import AuthLayout from '@/layouts/AuthLayout.vue';
import MainLayout from '@/layouts/MainLayout.vue';

const route = useRoute();

const layoutComponent = shallowRef(MainLayout); // MainLayout по умолчанию

watch(
  () => route.meta.layout,
  (newLayout) => {
    if (newLayout === 'AuthLayout') {
      layoutComponent.value = AuthLayout;
    } else {
      layoutComponent.value = MainLayout;
    }
  },
  { immediate: true } // Проверить сразу при загрузке
);
</script>