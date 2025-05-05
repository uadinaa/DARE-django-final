<template>
    <div>admin profile works</div>

  <BaseProfile :title="'Admin Profile'">
    <h2>Admin Tools</h2>
    <button @click="manageUsers">Manage Users</button>
    <button @click="viewAnalytics">View Analytics</button>
  </BaseProfile>
</template>

<script setup>
  import BaseProfile from './BaseProfile.vue';

  const manageUsers = () => {
    alert('Navigating to user management...');
  };

  const viewAnalytics = () => {
    alert('Viewing site analytics...');
  };
</script>
