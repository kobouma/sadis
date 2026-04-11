#!/usr/bin/env bash
set -e

echo "==> Installation des dépendances"
pip install -r requirements.txt

echo "==> Collecte des fichiers statiques"
DJANGO_SETTINGS_MODULE=config.settings.prod python manage.py collectstatic --no-input

echo "==> Migrations"
DJANGO_SETTINGS_MODULE=config.settings.prod python manage.py migrate --no-input

echo "==> Build terminé ✅"