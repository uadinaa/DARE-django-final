import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://139.59.64.140:8000/api', // Ваш базовый URL API
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

// Можно также добавить интерцептор ответов для обработки, например, ошибки 401 (не авторизован)
// apiClient.interceptors.response.use(
//   response => response,
//   error => {
//     if (error.response && error.response.status === 401) {
//       // Например, удалить токен и перенаправить на страницу входа
//       localStorage.removeItem('accessToken');
//       localStorage.removeItem('refreshToken');
//       // router.push({ name: 'Login' }); // Понадобится импортировать router сюда
//       // Или просто перезагрузить страницу, чтобы сработали навигационные хуки
//       window.location.href = '/login';
//       console.error("Unauthorized, redirecting to login.");
//     }
//     return Promise.reject(error);
//   }
// );

export default apiClient;