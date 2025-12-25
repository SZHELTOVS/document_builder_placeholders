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

# Копируем entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# ТОЛЬКО entrypoint - CMD не нужен
ENTRYPOINT ["/entrypoint.sh"]
