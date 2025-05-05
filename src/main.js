// src/main.js
import { createApp } from 'vue'

// 1. Импортируем Bootstrap ПЕРВЫМ
import 'bootstrap/dist/css/bootstrap.min.css'

// 2. Импортируем ВАШИ глобальные стили (если они есть)
import './style.css' // Убедитесь, что путь правильный (src/style.css)

// 3. Импортируем App ПОСЛЕ стилей
import App from './App.vue'

// Удаляем импорт './assets/main.css', он больше не нужен

import router from './router'
// Удаляем импорт './assets/main.css', он больше не нужен

// createApp(App).mount('#app')
const app = createApp(App)

app.use(router)
app.mount('#app')
