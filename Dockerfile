FROM python:3.12-slim

# Устанавливаем системные пакеты, необходимые для сборки psycopg2 из исходников
RUN apt-get update && \
    apt-get install -y libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# Переносим файл с зависимостями в контейнер
WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY . /app

# Запускаем приложение (пример, можно изменить под свои нужды)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]