FROM python:3.11-slim

WORKDIR /app

# Устанавливаем netcat для проверки доступности Postgres
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Или оставить простой CMD как запасной вариант
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]