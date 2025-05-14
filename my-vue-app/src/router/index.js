import { createRouter, createWebHistory } from 'vue-router';

import HomePage from '@/views/HomePage.vue';
import RegisterPage from '@/views/RegisterPage.vue';
import LoginPage from '@/views/LoginPage.vue';
import ProfilePage from '@/views/ProfilePage.vue';
import ProfileEditPage from '@/views/ProfileEditPage.vue';
import FollowingListPage from '@/views/FollowingListPage.vue';
import FollowersListPage from '@/views/FollowersListPage.vue';
import SettingsPage from '@/views/SettingsPage.vue';
import PostDetailPage from '@/views/PostDetailPage.vue';
import UserDetailPage from '@/views/UserDetailPage.vue';
import BecomeTrainerPage from '@/views/BecomeTrainerPage.vue';
import TrainerStatsPage from "@/views/TrainerStatsPage.vue";

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
    path: '/profile',
    name: 'profile',
    component: ProfilePage,
    meta: { layout: 'MainLayout', requiresAuth: true }
  },
  {
    path: '/profile/edit',
    name: 'profile-edit',
    component: ProfileEditPage,
    meta: { layout: 'MainLayout', requiresAuth: true }
  },
  {
    path: '/become-trainer',
    name: 'become-trainer-verification',
    component: BecomeTrainerPage,
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
  {
    path: '/users/:userId', // :userId - это параметр для ID пользователя
    name: 'user-detail',
    component: UserDetailPage,
    props: true,
    meta: { layout: 'MainLayout', requiresAuth: true }
  },
  {
    path: '/users/:userId/following',
    name: 'user-following',
    component: FollowingListPage,
    props: true,
    meta: { layout: 'MainLayout', requiresAuth: true }
  },
  {
    path: '/users/:userId/followers',
    name: 'user-followers',
    component: FollowersListPage,
    props: true,
    meta: { layout: 'MainLayout', requiresAuth: true }
  },
  {
    path: '/users/:userId/stats',
    name: 'users-stats',
    component: TrainerStatsPage,
    props: true,
    meta: { layout: 'MainLayout', requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('../views/ChatBot.vue'),
    meta: { layout: 'MainLayout', requiresAuth: true }
  }
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
