FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY app/ ./app/

# Создание директорий для данных
RUN mkdir -p /app/data /uploads /backups

# Expose port
EXPOSE 80

# Run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
