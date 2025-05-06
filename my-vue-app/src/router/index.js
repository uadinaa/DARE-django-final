// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import RegisterForm from '@/components/RegisterForm.vue'
import LoginForm from '../components/LoginForm.vue';
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
      component: AllPostsFeed, 
      meta: { requiresAuth: true } 
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterForm //maybe later we should create the welcoming page? or modify the register page to be more welcoming
    },
    {
      path: '/login',
      name: 'login',
      component: LoginForm
    },
    {
      path: '/user-profile',
      name: 'user-profile',
      component: UserPage
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

export default router;
