<script setup>
import { Line } from 'vue-chartjs'
import { ref, onMounted, watch } from 'vue'
import BaseProfile from './BaseProfile.vue';
import { ref, onMounted } from 'vue';
import axios from 'axios';
import SubscriberGrowthChart from '../components/SubscriberGrowthChart.vue'; // Import the chart component

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
)

const profile = ref(null);
const subscriberData = ref(null); // Data for the chart
const API_URL = '/api/users/trainer-profile/';
const props = defineProps({
    chartData: {
        type: Object,
        required: true
    },
    chartOptions: {
        type: Object,
        default: () => ({
            responsive: true,
        })
    }
})

const chartRef = ref(null)
const chartInstance = ref(null)

onMounted(async () => {
  try {
    renderChart()
    const response = await axios.get(API_URL);
    profile.value = response.data;
    await fetchSubscriberData(); // Fetch chart data on mount
  } catch (error) {
    console.error('Error fetching profile:', error);
  }
});

watch(
    () => props.chartData,
    () => {
        if (chartInstance.value) {
            chartInstance.value.destroy()
        }
        renderChart()
    },
    { deep: true }
)

const renderChart = () => {
    chartInstance.value = new ChartJS(chartRef.value, {
        type: 'line',
        data: props.chartData,
        options: props.chartOptions
    })
}

defineExpose({ chartInstance })

const fetchSubscriberData = async () => {
  try {
    const response = await axios.get(`/api/users/${profile.value.id}/subscriber_growth/`);
    subscriberData.value = {
      labels: response.data.labels,
      datasets: [{
        label: 'Subscribers',
        data: response.data.counts,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.4
      }]
    };
  } catch (error) {
    console.error('Error fetching subscriber data:', error);
  }
};

const managePosts = () => {
  alert('Navigating to post management...');
};

const viewStats = () => {
  alert('Viewing trainer statistics...');
};

</script>

<template>
  <div>
    trainer profile works
    <BaseProfile :title="'Trainer Profile'">
      <h2>Trainer Specifics</h2>
      <p>Role Display: {{ profile.role_display }}</p>
      <button @click="managePosts">Manage Posts</button>
      <button @click="viewStats">View Stats</button>

      <div v-if="subscriberData">
        <h3>Subscriber Growth (Last 30 Days)</h3>
        <SubscriberGrowthChart :chart-data="subscriberData" />
      </div>
    </BaseProfile>
  </div>
</template>
