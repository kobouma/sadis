#!/usr/bin/env bash
set -e

echo "==> Installation des dépendances"
pip install -r requirements/prod.txt

echo "==> Collecte des fichiers statiques"
python -c "
import sys, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.prod'
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'collectstatic', '--no-input'])
"

echo "==> Migrations"
python -c "
import sys, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.prod'
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'migrate', '--no-input'])
"

echo "==> Création superuser"
python -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.prod'
import django
django.setup()
from apps.users.models import User
phone    = os.environ.get('ADMIN_PHONE', '+22600000000')
name     = os.environ.get('ADMIN_NAME', 'Admin SADIS')
password = os.environ.get('ADMIN_PASSWORD', '')
if not password:
    print('ADMIN_PASSWORD non défini — skipped')
elif User.objects.filter(phone=phone).exists():
    print(f'Superuser existe déjà : {phone}')
else:
    User.objects.create_superuser(phone=phone, full_name=name, password=password)
    print(f'Superuser créé : {phone}')
"

echo "==> Build terminé ✅"