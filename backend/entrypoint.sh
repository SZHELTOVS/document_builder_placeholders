#!/bin/sh
set -e

echo "Waiting for PostgreSQL to start..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "PostgreSQL started successfully!"

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting Django server..."
exec "$@"