from datetime import timedelta
from pathlib import Path
import os

from dotenv import load_dotenv
import dj_database_url
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# -----------------------------
# Security / Env
# -----------------------------
SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
CUSTOM_DOMAIN = os.getenv("CUSTOM_DOMAIN")

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Render hostname (if available)
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Explicit domains + wildcard safety
ALLOWED_HOSTS += [
    "electro-backend-f1rh.onrender.com",
    "electro-back-5.onrender.com",
    ".onrender.com",  # ✅ IMPORTANT: allows any onrender subdomain
]

if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -----------------------------
# Firebase credentials (optional local file)
# -----------------------------
firebase_path = BASE_DIR / "secrets" / "firebase-admin.json"
if firebase_path.exists():
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(firebase_path))

# -----------------------------
# Razorpay / Twilio / Email
# -----------------------------
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_VERIFY_SID = os.getenv("TWILIO_VERIFY_SID", "")
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID", "")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# -----------------------------
# Apps
# -----------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",

    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",

    "catalog",
    "user",
]

# -----------------------------
# Middleware (Correct order)
# -----------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # ✅ CORS must be before CommonMiddleware
    "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# -----------------------------
# Database (SQLite local, Postgres on Render)
# -----------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# -----------------------------
# Auth / User
# -----------------------------
AUTH_USER_MODEL = "user.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------
# i18n
# -----------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -----------------------------
# Static / Media
# -----------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.getenv("STATIC_ROOT", str(BASE_DIR / "staticfiles"))

MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT", str(BASE_DIR / "media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------
# DRF + JWT
# -----------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# -----------------------------
# CORS / CSRF (JWT, no cookies)
# -----------------------------
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://electro-w3wa.onrender.com",
]

# allow extra origins via env (comma-separated)
extra_origins = [o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]
for o in extra_origins:
    if o not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(o)

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
    "content-type",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://electro-w3wa.onrender.com",
]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# Optional URLs
BACKEND_URL = os.getenv("https://electro-backend-f1rh.onrender.com", "http://127.0.0.1:8000")
FRONTEND_LOGIN_URL = os.getenv("https://electro-w3wa.onrender.com", "http://localhost:5173/account/login")