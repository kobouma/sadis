# scripts/create_superuser.py
# Exécuté une seule fois pendant le build pour créer l'admin initial
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
django.setup()

from apps.users.models import User

ADMIN_PHONE    = os.environ.get("ADMIN_PHONE",    "+2266795731")
ADMIN_NAME     = os.environ.get("ADMIN_NAME",     "Samurai")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "qwerty123")

if not ADMIN_PASSWORD:
    print("⚠️  ADMIN_PASSWORD non défini — superuser non créé.")
else:
    if not User.objects.filter(phone=ADMIN_PHONE).exists():
        User.objects.create_superuser(
            phone=ADMIN_PHONE,
            full_name=ADMIN_NAME,
            password=ADMIN_PASSWORD,
        )
        print(f"✅ Superuser créé : {ADMIN_PHONE}")
    else:
        print(f"ℹ️  Superuser existe déjà : {ADMIN_PHONE}")