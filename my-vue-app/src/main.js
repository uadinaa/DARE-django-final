import { createApp } from 'vue'

// 1. Импортируем Bootstrap ПЕРВЫМ
import 'bootstrap/dist/css/bootstrap.min.css'

// 2. Импортируем ВАШИ глобальные стили (если они есть)
import './style.css' // Убедитесь, что путь правильный (src/style.css)

// 3. Импортируем App ПОСЛЕ стилей
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(router)
app.mount('#app')
