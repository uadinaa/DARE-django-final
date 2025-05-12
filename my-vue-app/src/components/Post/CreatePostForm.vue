<template>
  <div class="create-post-form-minimal mb-4"> <form @submit.prevent="handleSubmitPost">
      <div v-if="errorMessage" class="alert alert-danger small p-2" role="alert">
        {{ errorMessage }}
      </div>
      <div v-if="successMessage" class="alert alert-success small p-2" role="alert">
        {{ successMessage }}
      </div>

      <div class="mb-3">
        <textarea 
          id="postContent" 
          class="form-control form-control-dark" 
          rows="3" 
          v-model="formData.content" 
          required
          placeholder="Что у вас нового?"
        ></textarea>
      </div>

      <div class="d-flex justify-content-between align-items-center">
        <div class="attachment-icons">
          <button type="button" @click="triggerImageUpload" class="btn btn-link text-light p-0 me-2" title="Прикрепить изображение">
            <i class="bi bi-paperclip fs-4"></i></button>
          </div>
        <button type="submit" :disabled="loading" class="btn btn-success fw-bold">
          {{ loading ? 'Публикация...' : 'Опубликовать' }}
        </button>
      </div>

      <input 
        type="file" 
        id="postImageUpload" 
        ref="imageInput" 
        @change="handleImageUpload" 
        accept="image/*" 
        style="display: none;"
      />
      <div v-if="imagePreviewUrl" class="mt-2 image-preview-container">
        <img :src="imagePreviewUrl" alt="Предпросмотр" class="img-thumbnail">
        <button type="button" @click="removeImage" class="btn btn-sm btn-danger remove-preview-btn">&times;</button>
      </div>
      </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import apiClient from '@/services/api';

const emit = defineEmits(['post-created']);

const formData = reactive({
  content: '',
  image: null,
  // video: null, // Убрали видео
});

const imagePreviewUrl = ref(null);
// const videoFileName = ref(''); // Убрали видео

const imageInput = ref(null); // ref для скрытого input type="file"
// const videoInput = ref(null); // Убрали видео

const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

const triggerImageUpload = () => {
  imageInput.value?.click(); // Программный клик по скрытому инпуту
};

// const triggerVideoUpload = () => { // Убрали видео
//   videoInput.value?.click();
// };

const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    formData.image = file;
    const reader = new FileReader();
    reader.onload = (e) => { imagePreviewUrl.value = e.target.result; };
    reader.readAsDataURL(file);
  } else {
    removeImage();
  }
};

const removeImage = () => {
  formData.image = null;
  imagePreviewUrl.value = null;
  if (imageInput.value) imageInput.value.value = ''; // Сбрасываем значение инпута
};

// Функции для видео убраны, так как вы отказались от поддержки видео
// const handleVideoUpload = (event) => { ... };
// const removeVideo = () => { ... };

const handleSubmitPost = async () => {
  loading.value = true; errorMessage.value = ''; successMessage.value = '';
  const postData = new FormData();
  postData.append('content', formData.content);
  if (formData.image) {
    postData.append('image', formData.image);
  }
  // if (formData.video) { // Убрали видео
  //   postData.append('video', formData.video);
  // }

  try {
    const response = await apiClient.post('/posts/', postData);
    successMessage.value = 'Пост успешно опубликован!';
    emit('post-created', response.data);
    formData.content = '';
    removeImage();
    // removeVideo(); // Убрали видео
    setTimeout(() => { successMessage.value = ''; }, 3000);
  } catch (error) {
    // ... (обработка ошибок как раньше)
    if (error.response && error.response.data) {
      const errors = error.response.data;
      let messages = [];
      for (const key in errors) {
        if (Array.isArray(errors[key])) { messages.push(`${key}: ${errors[key].join(', ')}`);}
        else { messages.push(`${key}: ${errors[key]}`);}
      }
      errorMessage.value = messages.join(' ') || 'Ошибка при публикации поста.';
    } else { errorMessage.value = 'Произошла ошибка сети или сервера при публикации.';}
    console.error('Error creating post:', error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.create-post-form-minimal {
  background-color: var(--color-card-bg-dark); /* Или другой подходящий фон */
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid var(--color-border-dark-theme);
}

.attachment-icons .btn-link {
  color: var(--vt-c-text-dark-2); /* Цвет иконок */
  text-decoration: none;
}
.attachment-icons .btn-link:hover i {
  color: var(--color-accent); /* Цвет иконок при наведении */
}

.image-preview-container {
  position: relative;
  display: inline-block; /* Чтобы кнопка удаления была рядом */
  margin-top: 0.5rem;
}
.image-preview-container .img-thumbnail {
  max-width: 100px; /* Маленький предпросмотр */
  max-height: 100px;
  border-color: var(--color-border-dark-theme);
}
.remove-preview-btn {
  position: absolute;
  top: -10px; /* Позиционируем кнопку удаления */
  right: -10px;
  border-radius: 50%;
  width: 25px;
  height: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  line-height: 1;
}
/* Используйте классы form-control-dark из вашего глобального style.css для textarea */
</style>