# Ajouter dans config/settings/base.py

from django.templatetags.static import static
from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE":  "SADIS",
    "SITE_HEADER": "SADIS Administration",
    "SITE_URL":    "/",
    "SITE_ICON": {
        "light": lambda request: static("icons/logo_dark.svg"),
        "dark":  lambda request: static("icons/logo_white.svg"),
    },
    "SITE_LOGO": {
        "light": lambda request: static("icons/logo_dark.svg"),
        "dark":  lambda request: static("icons/logo_white.svg"),
    },
    "SITE_SYMBOL": "store",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,

    # ── Thème couleurs SADIS ──────────────────────────────────
    "COLORS": {
        "font": {
            "subtle-light": "107 114 128",
            "subtle-dark":  "156 163 175",
            "default-light": "17 24 39",
            "default-dark":  "243 244 246",
            "important-light": "17 24 39",
            "important-dark":  "243 244 246",
        },
        "primary": {
            "50":  "255 245 245",
            "100": "255 220 220",
            "200": "255 180 180",
            "300": "255 140 140",
            "400": "255 100 100",
            "500": "255 49 49",    # #FF3131 — rouge SADIS
            "600": "220 30 30",
            "700": "185 15 15",
            "800": "150 5 5",
            "900": "120 0 0",
            "950": "90 0 0",
        },
    },

    # ── Sidebar ───────────────────────────────────────────────
    "SIDEBAR": {
        "show_search":     True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Navigation",
                "separator": False,
                "items": [
                    {
                        "title": "Tableau de bord",
                        "icon":  "dashboard",
                        "link":  reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Utilisateurs",
                "separator": True,
                "items": [
                    {
                        "title": "Utilisateurs",
                        "icon":  "people",
                        "link":  reverse_lazy("admin:users_user_changelist"),
                        "badge": "apps.users.admin.user_count",
                    },
                    {
                        "title": "Profils",
                        "icon":  "person",
                        "link":  reverse_lazy("admin:users_profile_changelist"),
                    },
                ],
            },
            {
                "title": "Marketplace",
                "separator": True,
                "items": [
                    {
                        "title": "Boutiques",
                        "icon":  "storefront",
                        "link":  reverse_lazy("admin:shops_shop_changelist"),
                    },
                    {
                        "title": "Catégories boutiques",
                        "icon":  "category",
                        "link":  reverse_lazy("admin:shops_shopcategory_changelist"),
                    },
                    {
                        "title": "Produits",
                        "icon":  "inventory_2",
                        "link":  reverse_lazy("admin:products_product_changelist"),
                    },
                    {
                        "title": "Catégories produits",
                        "icon":  "label",
                        "link":  reverse_lazy("admin:products_category_changelist"),
                    },
                ],
            },
            {
                "title": "Commandes",
                "separator": True,
                "items": [
                    {
                        "title": "Commandes",
                        "icon":  "receipt_long",
                        "link":  reverse_lazy("admin:orders_order_changelist"),
                    },
                    {
                        "title": "Paniers",
                        "icon":  "shopping_cart",
                        "link":  reverse_lazy("admin:orders_cart_changelist"),
                    },
                ],
            },
            {
                "title": "Livraison",
                "separator": True,
                "items": [
                    {
                        "title": "Tickets livraison",
                        "icon":  "local_shipping",
                        "link":  reverse_lazy("admin:delivery_deliveryticket_changelist"),
                    },
                ],
            },
            {
                "title": "Communication",
                "separator": True,
                "items": [
                    {
                        "title": "Conversations",
                        "icon":  "forum",
                        "link":  reverse_lazy("admin:chat_conversation_changelist"),
                    },
                    {
                        "title": "Notifications",
                        "icon":  "notifications",
                        "link":  reverse_lazy("admin:notifications_notification_changelist"),
                    },
                ],
            },
            {
                "title": "Avis",
                "separator": True,
                "items": [
                    {
                        "title": "Avis produits",
                        "icon":  "star",
                        "link":  reverse_lazy("admin:reviews_review_changelist"),
                    },
                ],
            },
        ],
    },
}