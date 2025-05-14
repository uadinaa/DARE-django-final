// views/BecomeTrainerPage.vue
<template>
  <div class="container mt-4">
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card bg-dark text-light">
          <div class="card-body">
            <h4 class="card-title text-center mb-4">Стать тренером</h4>
            <p class="text-muted text-center mb-4">
              Загрузите документы, подтверждающие вашу личность и квалификацию.
            </p>

            <form @submit.prevent="submitVerificationRequest">
              <div class="mb-3">
                <label for="identityDocument" class="form-label">Удостоверение личности (паспорт, ID карта)</label>
                <input type="file" class="form-control form-control-dark" id="identityDocument" @change="handleFileChange($event, 'identity')" accept="image/*,.pdf" required>
                <div v-if="errors.identity_document" class="text-danger small mt-1">{{ errors.identity_document.join(', ') }}</div>
              </div>

              <div class="mb-3">
                <label for="qualificationDocument" class="form-label">Документ о квалификации (сертификат, диплом)</label>
                <input type="file" class="form-control form-control-dark" id="qualificationDocument" @change="handleFileChange($event, 'qualification')" accept="image/*,.pdf" required>
                 <div v-if="errors.qualification_document" class="text-danger small mt-1">{{ errors.qualification_document.join(', ') }}</div>
              </div>

              <div v-if="serverError" class="alert alert-danger_custom small p-2 mt-3">{{ serverError }}</div>
              <div v-if="successMessage" class="alert alert-success small p-2 mt-3">{{ successMessage }}</div>

              <div class="d-grid mt-4">
                <button type="submit" class="btn btn-lg btn-success" :disabled="isSubmitting">
                  <span v-if="isSubmitting" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                  {{ isSubmitting ? 'Отправка...' : 'Отправить на подтверждение' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import apiClient from '@/services/api';
import { useRouter } // Для редиректа после успеха
from 'vue-router';

const router = useRouter();
const identityDocumentFile = ref(null);
const qualificationDocumentFile = ref(null);
const isSubmitting = ref(false);
const serverError = ref(null);
const successMessage = ref(null);
const errors = ref({}); // Для ошибок валидации полей

const handleFileChange = (event, docType) => {
  const file = event.target.files[0];
  if (file) {
    if (docType === 'identity') {
      identityDocumentFile.value = file;
    } else if (docType === 'qualification') {
      qualificationDocumentFile.value = file;
    }
  }
};

const submitVerificationRequest = async () => {
  if (!identityDocumentFile.value || !qualificationDocumentFile.value) {
    serverError.value = "Пожалуйста, загрузите оба документа.";
    return;
  }

  isSubmitting.value = true;
  serverError.value = null;
  successMessage.value = null;
  errors.value = {};

  const formData = new FormData();
  formData.append('identity_document', identityDocumentFile.value);
  formData.append('qualification_document', qualificationDocumentFile.value);

  try {
    const response = await apiClient.post('/users/me/request-trainer-verification/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    successMessage.value = "Ваша заявка успешно отправлена на рассмотрение!";
    // Опционально: редирект на страницу профиля через 2-3 секунды
    setTimeout(() => {
      router.push({ name: 'profile' }); // Или имя вашего маршрута для своего профиля
    }, 3000);

  } catch (error) {
    console.error("Ошибка отправки заявки:", error);
    if (error.response && error.response.data) {
        if (typeof error.response.data === 'string') {
             serverError.value = error.response.data;
        } else if (error.response.data.detail) {
             serverError.value = error.response.data.detail;
        }
        else {
            errors.value = error.response.data; // Ошибки валидации с бэка
            serverError.value = "Ошибка валидации. Проверьте поля.";
        }
    } else {
      serverError.value = "Не удалось отправить заявку. Попробуйте позже.";
    }
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* Стили для страницы верификации, используй свои CSS переменные */
.card.bg-dark {
  background-color: var(--vt-c-black-soft, #2a2a2e);
  border: 1px solid var(--color-border-dark-theme, #444);
}
.card-title {
  color: var(--color-accent, #42b983);
}
.form-label {
  color: var(--vt-c-text-dark-2, #bbb);
}
.text-danger {
    color: #dc3545 !important;
}
.alert-danger_custom { /* Твои стили для ошибок */
    color: #f8d7da;
    background-color: #4e2227;
    border-color: #f5c6cb;
}
.alert-success {
    color: #d1e7dd;
    background-color: #0f5132;
    border-color: #badbcc;
}
</style>