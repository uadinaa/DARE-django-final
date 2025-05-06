<template>
  <AppHeader v-if="$route.name !== 'login' && $route.name !== 'register'" />
  <router-view />
</template>
<script setup>
import AppHeader from './components/AppHeader.vue';
</script>

<style>
/* Глобальные стили можно оставить в style.css или перенести сюда, если они специфичны для App.vue */
/* Например, можно задать минимальную высоту для контентной области, чтобы футер (если будет) прижимался книзу */
.main-content-area {
  min-height: calc(100vh - 56px - 1rem - 1rem); /* 56px - примерная высота хедера, 1rem*2 - паддинги */
  /* Это очень приблизительный расчет, лучше использовать flexbox для layout всей страницы, если нужен "липкий" футер */
}
</style>
<!--<script setup>-->
<!--import { ref } from 'vue';-->
<!--import RegisterForm from './components/RegisterForm.vue';-->
<!--import LoginForm from './components/LoginForm.vue';-->

<!--const showLogin = ref(false);-->

<!--function switchToLoginHandler() {-->
<!--  showLogin.value = true;-->
<!--}-->

<!--function switchToRegisterHandler() {-->
<!--  showLogin.value = false;-->
<!--}-->
<!--</script>-->

<!--<template>-->
<!--  <LoginForm v-if="showLogin" @switchToRegister="switchToRegisterHandler" />-->
<!--  <RegisterForm v-else @switchToLogin="switchToLoginHandler" />-->
<!--</template>-->
