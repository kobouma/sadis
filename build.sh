#!/usr/bin/env bash
set -e

export DJANGO_SETTINGS_MODULE=config.settings.prod

echo "==> Installation des dépendances"
pip install -r requirements/prod.txt

echo "==> Debug settings"
python -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.prod'
import django
django.setup()
from django.conf import settings
print('SETTINGS MODULE:', os.environ.get('DJANGO_SETTINGS_MODULE'))
print('INSTALLED_APPS:', settings.INSTALLED_APPS)
print('DEBUG:', settings.DEBUG)
"

echo "==> Collecte des fichiers statiques"
python manage.py collectstatic --no-input

echo "==> Migrations"
python manage.py migrate --no-input

echo "==> Build terminé ✅"