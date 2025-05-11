<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4 fixed-top">
      <div class="container-fluid">
        <router-link class="navbar-brand" :to="{ name: 'home' }">
          <img src="@/assets/logo.svg" alt="Логотип Платформы" style="height: 30px; margin-right: 10px;">
          </router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavAuth"
          aria-controls="navbarNavAuth" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNavAuth">
          <ul class="navbar-nav ms-auto"> <li class="nav-item">
              <router-link class="nav-link" :to="{ name: 'login' }"
                active-class="active">Вход</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :to="{ name: 'register' }"
                active-class="active">Регистрация</router-link>
            </li>
            </ul>
        </div>
      </div>
    </nav>
  </template>
  
  <script setup>
  </script>
  
  <style scoped>
  /* Стили можно оставить или адаптировать, если нужно */
  .navbar {
    box-shadow: 0 2px 4px rgba(0, 0, 0, .1);
  }
  
  .nav-link.active {
    font-weight: bold;
    color: #ffffff !important; /* Убедитесь, что Bootstrap не переопределяет это */
  }
  
  .navbar-nav .nav-item {
    display: flex;
    align-items: center;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
  
  </style>