<template>
     <BaseProfile :title="'User Profile'">
       <div v-if="profile">
         <div class="avatar-container">
           <img
              :src="profile.avatar || defaultAvatar"
               alt="User Avatar"
               class="avatar" />
         </div>
           <input type="file" @change="changeAvatar" accept="image/*" />
           <button @click="uploadAvatar" v-if="selectedAvatar">Upload Avatar</button>
           <button @click="cancelAvatar" v-if="selectedAvatar">Cancel</button>

         <h2>basic info</h2>
         <p>Username: {{ profile.username }}</p>
         <p>Email: {{ profile.email }}</p>

         <h2>about me/goals</h2>
           <p v-if="!editingBio">{{ profile.bio || 'Нет информации' }}</p>
           <textarea v-if="editingBio" v-model="editableBio"></textarea>
           <button v-if="!editingBio" @click="startEditBio">Редактировать</button>
           <button v-if="editingBio" @click="saveBio">Сохранить</button>
           <button v-if="editingBio" @click="cancelEditBio">Отмена</button>

       </div>
       <div v-else>
         Loading profile...
       </div>
     </BaseProfile>
</template>

<script setup>
   import BaseProfile from './BaseProfile.vue';
   import { ref, onMounted } from 'vue';
   import axios from 'axios';
   import { useRouter } from 'vue-router'; // Import useRouter
   import defaultAvatar from '@/assets/cuteAva.jpg';

   const profile = ref(null);
   // const API_URL = '/api/users/profiles/';
   const API_URL = 'http://ec2-13-53-50-251.eu-north-1.compute.amazonaws.com:8000/api/users/me';
   const router = useRouter();  // Initialize useRouter
   const editingBio = ref(false);
   const editableBio = ref('');
   // const defaultAvatar = '@/assets/cute.png'; // Путь к изображению по умолчанию
   const selectedAvatar = ref(null); // To store the selected file

   onMounted(async () => {
     try {
       const token = localStorage.getItem('access_token');
       if (!token) {
         router.push('/login'); // Redirect if no token (or expired)
         return;
       }

       const response = await axios.get(API_URL, {
         headers: { Authorization: `Bearer ${token}` }  // Include the token
       });
       profile.value = response.data;

       console.log('API Response:', response.data); //  DEBUG: Log the whole response
       if (profile.value && profile.value.avatar) {
         console.log('Avatar URL:', profile.value.avatar); //  DEBUG: Log avatar URL
       }

     } catch (error) {
       console.error('Error fetching profile:', error);
       router.push('/login'); // Redirect on error
     }
   });

   const startEditBio = () => {
     editingBio.value = true;
     editableBio.value = profile.value.bio;
   };

   const cancelEditBio = () => {
     editingBio.value = false;
     editableBio.value = '';
   };

   const saveBio = async () => {
     try {
       const token = localStorage.getItem('access_token');
       if (!token) {
         router.push('/login');
         return;
       }

       await axios.patch(API_URL, { bio: editableBio.value }, {
         headers: { Authorization: `Bearer ${token}` },
       });
       profile.value.bio = editableBio.value;
       editingBio.value = false;
       alert('Bio updated!');
     } catch (error) {
       console.error('Error updating bio:', error);
     }
   };
   const changeAvatar = (event) => {
     const file = event.target.files[0];
     selectedAvatar.value = file;
   };

   const uploadAvatar = async () => {
     if (!selectedAvatar.value) {
       alert('Please select an avatar to upload.');
       return;
     }

     try {
       const token = localStorage.getItem('access_token');
       if (!token) {
         router.push('/login');
         return;
       }

       const formData = new FormData();
       formData.append('avatar', selectedAvatar.value); // 'avatar' must match your Django field name

       await axios.patch(API_URL, formData, {
         headers: {
           Authorization: `Bearer ${token}`,
           'Content-Type': 'multipart/form-data', //  Important for file uploads
         },
       });

       //  Optionally, refresh the profile data to show the new avatar
       await fetchProfileData(); //  Create this function to re-fetch profile
       alert('Avatar updated!');
     } catch (error) {
       console.error('Error uploading avatar:', error);
       alert('Error uploading avatar.');
     }
   };

   const cancelAvatar = () => {
    selectedAvatar.value = null; // Clear the selected file
   };

   const fetchProfileData = async () => {
     try {
       const token = localStorage.getItem('access_token');
       if (!token) {
         router.push('/login');
         return;
       }

       const response = await axios.get(API_URL, {
         headers: { Authorization: `Bearer ${token}` },
       });
       profile.value = response.data;
     } catch (error) {
       console.error('Error fetching profile data:', error);
     }
   };

</script>

<style scoped>
  .avatar-container {
  width: 300px;
  height: 300px;
  border-radius: 50%;
  overflow: hidden;
  margin-bottom: 15px;
  border: 3px solid #fff;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover; /* Important for scaling */
}
</style>

