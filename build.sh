#!/usr/bin/env bash
set -e

# Forcer le settings prod pour tout le script
export DJANGO_SETTINGS_MODULE=config.settings.prod

echo "==> Installation des dépendances"
pip install -r requirements/prod.txt

echo "==> Vérification Django"
python -c "import django; django.setup(); print('Django OK', django.__version__)"

echo "==> Collecte des fichiers statiques"
python manage.py collectstatic --no-input

echo "==> Migrations"
python manage.py migrate --no-input

echo "==> Build terminé ✅"