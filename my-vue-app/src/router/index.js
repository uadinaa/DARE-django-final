import { createRouter, createWebHistory } from 'vue-router';
import RegisterPage from '@/views/RegisterPage.vue'
import LoginPage from '../views/LoginPage.vue';
import HomePage from '@/views/HomePage.vue'; // Ваш AllPostsFeed
import ProfilePage from '@/views/ProfilePage.vue';
import SettingsPage from '@/views/SettingsPage.vue';
import PostDetailPage from '@/views/PostDetailPage.vue';
import UserPage from '../components/Profile/UserProfile.vue';
// import ProfilePage from '@/components/ProfilePage.vue';
import TrainerPage from '@/components/Profile/TrainerPage.vue';
import AdminPage from '@/components/Profile/AdminPage.vue'
import AllPostsFeed from '@/views/AllPostsFeed.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home', 
      component: HomePage, 
      meta: { requiresAuth: true } 
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterPage, //maybe later we should create the welcoming page? or modify the register page to be more welcoming
      meta: { layout: 'AuthLayout' }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { layout: 'AuthLayout' }
    },
    {
      path: '/user-profile',
      name: 'user-profile',
      component: UserPage
    },
    {
      path: '/profile',
      name: 'profile',
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
      path: '/posts/:id',
      name: 'post-detail',
      component: PostDetailPage,
      props: true,
      meta: { layout: 'MainLayout', requiresAuth: true }
    },
    {
      path: '/trainer-profile',
      name: 'trainer-profile',
      component: TrainerPage
    },
    {
      path: '/admin-profile',
      name: 'admin-profile',
      component: AdminPage
    },
    // {
    //   path: '/profile',
    //   name: 'profile',
    //   component: ProfilePage
    // },
  ]
});

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const isLoggedIn = !!localStorage.getItem('accessToken'); // Простая проверка токена

  if (requiresAuth && !isLoggedIn) {
    next({ name: 'login' });
  } else {
    next();
  }
});

export default router;
