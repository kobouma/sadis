#!/usr/bin/env bash
set -e

export DJANGO_SETTINGS_MODULE=config.settings.prod

echo "==> Installation des dépendances"
pip install -r requirements/prod.txt

echo "==> Collecte des fichiers statiques"
python manage.py collectstatic --no-input

echo "==> Migrations"
python manage.py migrate --no-input

echo "==> Création superuser"
python manage.py shell -c "
from apps.users.models import User
import os
phone    = os.environ.get('ADMIN_PHONE', '+22665795731')
name     = os.environ.get('ADMIN_NAME', 'Admin SADIS')
password = os.environ.get('ADMIN_PASSWORD', 'qwerty123')
if not password:
    print('⚠️  ADMIN_PASSWORD non défini — skipped')
elif User.objects.filter(phone=phone).exists():
    print(f'ℹ️  Superuser existe déjà : {phone}')
else:
    User.objects.create_superuser(phone=phone, full_name=name, password=password)
    print(f'✅ Superuser créé : {phone}')
"

echo "==> Build terminé ✅"