#!/usr/bin/env bash
set -e

export DJANGO_SETTINGS_MODULE=config.settings.prod

echo "==> Installation des dépendances"
pip install -r requirements/prod.txt

echo "==> Collecte des fichiers statiques"
python manage.py collectstatic --no-input

echo "==> Migrations"
python manage.py migrate --no-input

echo "==> Création superuser (si ADMIN_PASSWORD défini)"
python scripts/create_superuser.py

echo "==> Build terminé ✅"