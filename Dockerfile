# Базовый образ с Python
FROM python:3.13-slim

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем всё остальное
COPY . .

# Указываем порт
EXPOSE 8050

# Команда запуска
CMD ["gunicorn", "app:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "8", "--bind", "0.0.0.0:8050", "--timeout", "180"]