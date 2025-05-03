# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем системные зависимости (если нужны, например, для Pillow или PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev netcat-traditional && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем pipenv (если используете) или копируем requirements.txt
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем код проекта в рабочую директорию
COPY . /app/

# Открываем порт, на котором будет работать Django
EXPOSE 8000
