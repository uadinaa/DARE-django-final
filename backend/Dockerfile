FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev netcat-traditional \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Кэш pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip

# Базовые зависимости
COPY requirements-base.txt /app/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements-base.txt

# Новые зависимости
COPY requirements-extra.txt /app/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-deps -r requirements-extra.txt

COPY . /app/

EXPOSE 8000