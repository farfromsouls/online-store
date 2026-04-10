#!/bin/sh

echo "Waiting for database..."
while ! python -c "import socket; s=socket.socket(); s.connect(('$DB_HOST', int('$DB_PORT'))); s.close()" 2>/dev/null; do
  sleep 1
done
echo "Database started"

if [ "$DEBUG" = "1" ]; then
    python manage.py makemigrations
fi
python manage.py migrate
python manage.py collectstatic --noinput

chmod -R 755 /app/staticfiles
chmod -R 755 /app/media

exec "$@"
