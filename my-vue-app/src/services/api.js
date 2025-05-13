import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://139.59.64.140:8000/api',
  // baseURL: 'http://localhost:8000/api',
});

// Интерцептор запросов: добавляет токен авторизации к каждому запросу, если он есть
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    // Список публичных путей, для которых токен не нужен
    const publicPaths = ['/token/', '/users/register/']; // Убедитесь, что пути соответствуют вашим API эндпоинтам

    if (token && !publicPaths.some(path => config.url.includes(path))) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default apiClient;
