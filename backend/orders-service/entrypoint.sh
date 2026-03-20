#!/bin/bash
set -euo pipefail

echo "[entrypoint] Attente de PostgreSQL..."
until /opt/venv/bin/python orders/manage.py inspectdb > /dev/null 2>&1; do
  echo "[entrypoint] DB pas encore prête, attente 2s..."
  sleep 2
done

echo "[entrypoint] DB prête. Migration..."
/opt/venv/bin/python orders/manage.py migrate --noinput

echo "[entrypoint] Démarrage Gunicorn..."
exec /opt/venv/bin/gunicorn --config orders/gunicorn.conf.py