#!/bin/bash
set -euo pipefail

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

echo "[entrypoint] DB prête. Migration..."
/opt/venv/bin/python auth/manage.py migrate --noinput

echo "[entrypoint] Démarrage Gunicorn..."
exec /opt/venv/bin/gunicorn --config auth/gunicorn.conf.py