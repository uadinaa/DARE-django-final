    FROM node:18-alpine AS build-stage

    WORKDIR /app
    
    # Копируем package.json и package-lock.json (или yarn.lock)
    COPY package*.json ./
    
    RUN npm install
    
    COPY . .
    
    RUN npm run build
    
    FROM nginx:stable-alpine
    
    # Копируем собранные статические файлы из стадии сборки в директорию Nginx
    COPY --from=build-stage /app/dist /usr/share/nginx/html
    
    COPY nginx.conf /etc/nginx/conf.d/default.conf
    
    # Открываем порт 80, на котором будет слушать Nginx
    EXPOSE 80
    
    CMD ["nginx", "-g", "daemon off;"]
