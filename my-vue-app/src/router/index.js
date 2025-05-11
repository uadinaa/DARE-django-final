// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';

// Views (страницы)
import HomePage from '@/views/HomePage.vue';
import RegisterPage from '@/views/RegisterPage.vue';
import LoginPage from '@/views/LoginPage.vue';
import ProfilePage from '@/views/ProfilePage.vue'; // Для своего профиля
import SettingsPage from '@/views/SettingsPage.vue';
import PostDetailPage from '@/views/PostDetailPage.vue';
import UserDetailPage from '@/views/UserDetailPage.vue'; // <-- НОВАЯ СТРАНИЦА для профиля другого пользователя

// Убираем дублирующийся импорт AllPostsFeed, если HomePage - это он
// import AllPostsFeed from '@/views/AllPostsFeed.vue';

// Убираем импорты компонентов, если они не используются как страницы напрямую
// import UserPage from '../components/Profile/UserProfile.vue';
// import TrainerPage from '@/components/Profile/TrainerPage.vue';
// import AdminPage from '@/components/Profile/AdminPage.vue'


const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
    meta: { layout: 'MainLayout', requiresAuth: true }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage,
    meta: { layout: 'AuthLayout' }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { layout: 'AuthLayout' }
  },
  {
    path: '/profile', // Маршрут для СВОЕГО профиля
    name: 'profile', // Это имя будет использоваться в AppSidebar.vue
    component: ProfilePage,
    meta: { layout: 'MainLayout', requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsPage,
    meta: { layout: 'MainLayout', requiresAuth: true }
  },
  {
    path: '/posts/:id', // :id это post_id
    name: 'post-detail',
    component: PostDetailPage,
    props: true,
    meta: { layout: 'MainLayout', requiresAuth: true }
  },
  // --- НОВЫЙ МАРШРУТ ДЛЯ ПРОСМОТРА ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ ПО ID ---
  {
    path: '/users/:userId', // :userId - это параметр для ID пользователя
    name: 'user-detail',   // Имя маршрута, используется в TopTrainer.vue
    component: UserDetailPage,
    props: true, // Позволяет передавать userId как props в компонент UserDetailPage
    meta: { layout: 'MainLayout', requiresAuth: true }
  }
  // -----------------------------------------------------------
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const isLoggedIn = !!localStorage.getItem('accessToken'); 

  if (requiresAuth && !isLoggedIn) {
    next({ name: 'login' });
  } else {
    next();
  }
});

export default router;