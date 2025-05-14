<template>
  <div>
    <canvas ref="chartRef" />
  </div>
</template>

<script setup>
import { Line } from 'vue-chartjs'
import { ref, onMounted, watch } from 'vue'
import {
Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
)

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

console.log('chartData в SubscriberGrowthChart:', props.chartData);

onMounted(() => {
    renderChart()
})

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
    if (chartRef.value && props.chartData) { // Проверяем, что ref существует и данные есть
        chartInstance.value = new ChartJS(chartRef.value, {
            type: 'line',
            data: props.chartData,
            options: props.chartOptions
        })
    }
}

defineExpose({ chartInstance })
</script>


