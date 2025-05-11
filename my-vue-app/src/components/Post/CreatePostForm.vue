<template>
    <div class="create-post-form card bg-dark text-light border-secondary p-3 mb-4 shadow-sm">
      <h5 class="card-title text-success mb-3">Создать новый пост</h5>
      <form @submit.prevent="handleSubmitPost">
        <div v-if="errorMessage" class="alert alert-danger small p-2" role="alert">
          {{ errorMessage }}
        </div>
        <div v-if="successMessage" class="alert alert-success small p-2" role="alert">
          {{ successMessage }}
        </div>
  
        <div class="mb-3">
          <label for="postContent" class="form-label">Текст поста:</label>
          <textarea 
            id="postContent" 
            class="form-control form-control-dark" 
            rows="4" 
            v-model="formData.content" 
            required
            placeholder="Поделитесь своими мыслями или советом..."
          ></textarea>
        </div>
  
        <div class="mb-3">
          <label for="postImage" class="form-label">Изображение (необязательно):</label>
          <input 
            type="file" 
            id="postImage" 
            class="form-control form-control-dark" 
            @change="handleImageUpload"
            accept="image/*" 
          />
          <div v-if="imagePreviewUrl" class="mt-2">
            <img :src="imagePreviewUrl" alt="Предпросмотр изображения" class="img-thumbnail" style="max-height: 150px;">
            <button type="button" @click="removeImage" class="btn btn-sm btn-outline-danger ms-2">Удалить</button>
          </div>
        </div>

        <button type="submit" :disabled="loading" class="btn btn-success w-100 fw-bold">
          {{ loading ? 'Публикация...' : 'Опубликовать' }}
        </button>
      </form>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive } from 'vue';
  import apiClient from '@/services/api';
  
  const emit = defineEmits(['post-created']); // Для оповещения родителя о новом посте
  
  const formData = reactive({
    content: '',
    image: null, // Будет хранить объект File
    video: null, // Будет хранить объект File
  });
  
  const imagePreviewUrl = ref(null);
  const videoFileName = ref('');
  
  const loading = ref(false);
  const errorMessage = ref('');
  const successMessage = ref('');
  
  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      formData.image = file;
      // Создаем URL для предпросмотра
      const reader = new FileReader();
      reader.onload = (e) => {
        imagePreviewUrl.value = e.target.result;
      };
      reader.readAsDataURL(file);
    } else {
      removeImage();
    }
  };
  
  const removeImage = () => {
    formData.image = null;
    imagePreviewUrl.value = null;
    // Очищаем input type="file", чтобы можно было выбрать тот же файл снова
    const imageInput = document.getElementById('postImage');
    if (imageInput) imageInput.value = '';
  };
  
  const handleVideoUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      formData.video = file;
      videoFileName.value = file.name;
    } else {
      removeVideo();
    }
  };
  
  const removeVideo = () => {
    formData.video = null;
    videoFileName.value = '';
    const videoInput = document.getElementById('postVideo');
    if (videoInput) videoInput.value = '';
  };
  
  const handleSubmitPost = async () => {
    loading.value = true;
    errorMessage.value = '';
    successMessage.value = '';
  
    // Используем FormData для отправки файлов
    const postData = new FormData();
    postData.append('content', formData.content);
    if (formData.image) {
      postData.append('image', formData.image);
    }
    if (formData.video) {
      postData.append('video', formData.video);
    }
  
    try {
      const response = await apiClient.post('/posts/', postData, {
        headers: {
          // 'Content-Type': 'multipart/form-data' // Axios обычно устанавливает это автоматически для FormData
        }
      });
      successMessage.value = 'Пост успешно опубликован!';
      emit('post-created', response.data); // Отправляем данные нового поста родителю
  
      // Очищаем форму
      formData.content = '';
      removeImage();
      removeVideo();
      // Можно скрыть сообщение об успехе через некоторое время
      setTimeout(() => { successMessage.value = ''; }, 3000);
  
    } catch (error) {
      if (error.response && error.response.data) {
        const errors = error.response.data;
        let messages = [];
        for (const key in errors) {
          if (Array.isArray(errors[key])) {
            messages.push(`${key}: ${errors[key].join(', ')}`);
          } else {
            messages.push(`${key}: ${errors[key]}`);
          }
        }
        errorMessage.value = messages.join(' ') || 'Ошибка при публикации поста.';
      } else {
        errorMessage.value = 'Произошла ошибка сети или сервера при публикации.';
      }
      console.error('Error creating post:', error);
    } finally {
      loading.value = false;
    }
  };
  </script>
  
  <style scoped>
  .create-post-form {
    /* Стили для самой формы, если нужны дополнительные */
    border-radius: 8px; /* Пример */
  }
  
  .img-thumbnail { /* Стили для предпросмотра изображения */
    max-width: 100%;
    height: auto;
    border: 1px solid var(--color-border-dark-theme); /* Используем переменную */
  }
  /* Используйте классы form-control-dark из вашего глобального style.css */
  </style>