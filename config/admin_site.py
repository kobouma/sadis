# config/admin_site.py
# Personnalisation globale du site admin Django
# Importer dans config/urls.py ou apps.py

from django.contrib import admin

admin.site.site_header  = "SADIS — Administration"
admin.site.site_title   = "SADIS Admin"
admin.site.index_title  = "Tableau de bord"