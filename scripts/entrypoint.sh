#!/bin/bash
set -e

echo "Waiting for database to be ready..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is ready!"

echo "Running database migrations..."
alembic upgrade head

echo "Starting the application..."
exec "$@"