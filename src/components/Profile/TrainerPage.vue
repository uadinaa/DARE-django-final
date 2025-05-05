   <template>
       <div>trainer profile works</div>

     <BaseProfile :title="'Trainer Profile'">
       <h2>Trainer Specifics</h2>
       <p>Role Display: {{ profile.role_display }}</p>
       <button @click="managePosts">Manage Posts</button>
       <button @click="viewStats">View Stats</button>
     </BaseProfile>
   </template>

   <script setup>
   import BaseProfile from './BaseProfile.vue';
   import { ref, onMounted } from 'vue';
   import axios from 'axios';

   const profile = ref(null);
   const API_URL = '/api/users/trainer-profile/'; // Adjust as needed

   onMounted(async () => {
     console.log('TrainerProfile.vue - onMounted'); //  <--  Add this

     try {
       const response = await axios.get(API_URL);
       console.log('TrainerProfile.vue - API Response:', response.data); //  <--  And this
       profile.value = response.data;
     } catch (error) {
       console.error('TrainerProfile.vue - Error fetching profile:', error); //  <--  And this
     }
   });

   const managePosts = () => {
     alert('Navigating to post management...');
   };

   const viewStats = () => {
     alert('Viewing trainer statistics...');
   };
   </script>

