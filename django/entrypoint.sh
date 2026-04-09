#!/bin/sh

echo "Waiting for database..."
while ! python -c "import socket; s=socket.socket(); s.connect(('$DB_HOST', int('$DB_PORT'))); s.close()" 2>/dev/null; do
  sleep 1
done
echo "Database started"

python manage.py makemigrations user
python manage.py makemigrations shop
python manage.py migrate
python manage.py collectstatic --noinput

exec "$@"
