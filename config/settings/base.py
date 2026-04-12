from pathlib import Path
from datetime import timedelta
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY    = env("SECRET_KEY", default="django-insecure-change-me")
DEBUG         = env("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

DJANGO_APPS = [
    "unfold",                          
    "unfold.contrib.filters",          
    "unfold.contrib.forms",
    "django.contrib.admin", "django.contrib.auth",
    "django.contrib.contenttypes", "django.contrib.sessions",
    "django.contrib.messages", "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = ["rest_framework", "rest_framework_simplejwt",
                    "corsheaders", "channels", "django_filters",
                    "cloudinary_storage", "cloudinary"]
LOCAL_APPS = ["apps.users", "apps.shops", "apps.products", "apps.orders",
              "apps.delivery", "apps.chat", "apps.tracking",
              "apps.notifications", "apps.reviews"]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF     = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates",
              "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
              "OPTIONS": {"context_processors": [
                  "django.template.context_processors.debug",
                  "django.template.context_processors.request",
                  "django.contrib.auth.context_processors.auth",
                  "django.contrib.messages.context_processors.messages"]}}]

DATABASES = {"default": {
    "ENGINE":   env("DB_ENGINE",   default="django.db.backends.sqlite3"),
    "NAME":     env("DB_NAME",     default=str(BASE_DIR / "db.sqlite3")),
    "USER":     env("DB_USER",     default=""),
    "PASSWORD": env("DB_PASSWORD", default=""),
    "HOST":     env("DB_HOST",     default=""),
    "PORT":     env("DB_PORT",     default=""),
}}

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES":     ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS":       "core.pagination.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend",
                                 "rest_framework.filters.SearchFilter",
                                 "rest_framework.filters.OrderingFilter"],
    "DEFAULT_RENDERER_CLASSES":  ["rest_framework.renderers.JSONRenderer"],
    "EXCEPTION_HANDLER": "core.exceptions.handlers.custom_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=env.int("JWT_ACCESS_MINUTES", default=60)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_DAYS", default=30)),
    "ROTATE_REFRESH_TOKENS":  True,
    "AUTH_HEADER_TYPES":      ("Bearer",),
}

CORS_ALLOWED_ORIGINS   = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"])
CORS_ALLOW_CREDENTIALS = True
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

LANGUAGE_CODE = "fr-fr"
TIME_ZONE     = "Africa/Ouagadougou"
USE_I18N      = True
USE_TZ        = True
STATIC_URL    = "/static/"
STATIC_ROOT   = BASE_DIR / "staticfiles"
MEDIA_URL     = "/media/"
MEDIA_ROOT    = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Cloudinary ────────────────────────────────────────────────
import cloudinary
import cloudinary.uploader
import cloudinary.api

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": env("CLOUDINARY_CLOUD_NAME", default=""),
    "API_KEY":    env("CLOUDINARY_API_KEY",    default=""),
    "API_SECRET": env("CLOUDINARY_API_SECRET", default=""),
    "SECURE":     True,
}

cloudinary.config(
    cloud_name = env("CLOUDINARY_CLOUD_NAME", default=""),
    api_key    = env("CLOUDINARY_API_KEY",    default=""),
    api_secret = env("CLOUDINARY_API_SECRET", default=""),
    secure     = True,
)

# Remplace le stockage local pour tous les médias
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

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
