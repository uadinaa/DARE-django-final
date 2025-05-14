<template>
  <div class="trainer-stats-page container py-4">
    <h3 class="text-success mb-3">Моя статистика тренера</h3>
    <SubscriberGrowthChart :chartData="myGrowthData" :chartOptions="chartOptions" />
    <button @click="$router.go(-1)" class="btn btn-sm btn-secondary mt-3">Назад к профилю</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import SubscriberGrowthChart from '@/views/SubscriberGrowthChart.vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const myGrowthData = ref(null);
const chartOptions = ref({ responsive: true });

const fetchTrainerStats = async () => {
  console.log('fetchTrainerStats вызвана на странице статистики');
  try {
    const response = await apiClient.get('/users/me/stats/');
    const labels = response.data.dailySubscribers.labels.slice().reverse();
    const counts = response.data.dailySubscribers.counts.slice().reverse();

    myGrowthData.value = {
      labels: labels,
      datasets: [
        {
          label: 'Новые подписчики',
          data: counts,
          borderColor: 'rgb(75, 168, 62)',
          tension: 0.1,
        },
      ],
    };
  } catch (err) {
    console.error('Ошибка при получении статистики тренера:', err);
  }
};

onMounted(() => {
  fetchTrainerStats();
});
</script>

<style scoped>
.trainer-stats-page {
  color: var(--vt-c-text-dark-1);
}
</style>
