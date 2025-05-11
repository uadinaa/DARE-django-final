   <template>
     <div class="profile-container">
       <header class="profile-header">
         <h1>{{ title }}</h1>
         </header>
       <main class="profile-main">
         <slot></slot>  </main>
     </div>
   </template>

   <script setup>
   import { ref } from 'vue';

   const title = ref('Profile'); // Default title
   </script>

   <style scoped>
   .profile-container {
       /* Dark background from src/style.css */
       background-image: linear-gradient(to bottom right, #1a3a24, #152133);
       color: #fff;
       min-height: 100vh;
       margin: 0;
       padding: 20px;
     }

     .profile-header {
       padding-bottom: 20px;
       border-bottom: 1px solid #fff;
     }

     .profile-main {
       margin-top: 20px;
     }

</style>
