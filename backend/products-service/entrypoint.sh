#!/bin/sh
set -eu

echo "[entrypoint] Attente de PostgreSQL sur ${DB_HOST}:${DB_PORT:-5432}..."
until /opt/venv/bin/python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=os.environ.get('DB_PORT', '5432'),
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
    )
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  echo "[entrypoint] DB pas encore prête, attente 2s..."
  sleep 2
done

echo "[entrypoint] Création des migrations..."
/opt/venv/bin/python products/manage.py makemigrations --noinput

echo "[entrypoint] DB prête. Migration..."
/opt/venv/bin/python products/manage.py migrate --noinput

echo "[entrypoint] Création du superuser si inexistant..."
/opt/venv/bin/python products/manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='${DJANGO_SUPERUSER_EMAIL:-admin@admin.com}',
        password='${DJANGO_SUPERUSER_PASSWORD:-admin123}',
        username='${DJANGO_SUPERUSER_USERNAME:-admin}'
    )
    print('[entrypoint] ✅ Superuser créé')
else:
    print('[entrypoint] ℹ️  Superuser existe déjà, skip')
"

echo "[entrypoint] Collecte des fichiers statiques..."
/opt/venv/bin/python products/manage.py collectstatic --noinput

echo "[entrypoint] Démarrage Gunicorn..."
exec /opt/venv/bin/gunicorn --config products/gunicorn.conf.py