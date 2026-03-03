import os
from pathlib import Path
import dj_database_url
from datetime import timedelta
from corsheaders.defaults import default_headers

from .settings import *

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------- SECURITY ----------------

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", SECRET_KEY)

RENDER_HOST = os.getenv("RENDER_EXTERNAL_HOSTNAME")

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)

# Optional custom domain
CUSTOM_DOMAIN = os.getenv("CUSTOM_DOMAIN")
if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)

# ---------------- CSRF ----------------
# Only matters if you use cookies/session/CSRF-protected requests.
CSRF_TRUSTED_ORIGINS = [
    "https://electro-w3wa.onrender.com",            # ✅ your current frontend
    "https://electromdoules-frontend.onrender.com",
    "https://electromodules.shop",
]
if RENDER_HOST:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_HOST}")

# ---------------- Razorpay ----------------

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# ---------------- Middleware ----------------
# Recommended: Security -> CORS -> WhiteNoise -> Session -> Common -> CSRF...

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------------- Static files ----------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# ---------------- Database ----------------

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
# else: fallback stays from base settings (sqlite)

# ---------------- CORS ----------------

CORS_ALLOW_CREDENTIALS = True

extra_origins = [o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]

CORS_ALLOWED_ORIGINS = list(dict.fromkeys([
    *extra_origins,
    "https://electro-w3wa.onrender.com",            # ✅ your current frontend
    "https://electromdoules-frontend.onrender.com",
    "https://electromodules.shop",
    "http://localhost:5173",
]))

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
    "content-type",
    "x-csrftoken",
]

# ---------------- JWT ----------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------- Media ----------------

MEDIA_URL = "/media/"
MEDIA_ROOT = "/var/data/media"

# ---------------- Email (SMTP) ----------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER