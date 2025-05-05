<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>

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
