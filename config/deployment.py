import os
from pathlib import Path
import dj_database_url
from datetime import timedelta
from corsheaders.defaults import default_headers

# Import base settings (your main settings.py)
from .settings import *

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------- SECURITY ----------------

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

SECRET_KEY = os.getenv("SECRET_KEY", SECRET_KEY)

# Render hostname (e.g. electro-back-5.onrender.com)
RENDER_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)

# If you have a custom domain:
CUSTOM_DOMAIN = os.getenv("CUSTOM_DOMAIN")  # e.g. "electromodules.shop"
if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)

# ---------------- CSRF ----------------

CSRF_TRUSTED_ORIGINS = []

if RENDER_HOST:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_HOST}")

# Your frontend domains
CSRF_TRUSTED_ORIGINS += [
    "https://electro-w3wa.onrender.com",
    "https://electromdoules-frontend.onrender.com",
    "https://electromodules.shop",
]

# ---------------- Middleware ----------------
# Ensure cors middleware is at the top (before CommonMiddleware)

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
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
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

# ---------------- Database ----------------

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("DATABASE_URL is not set")

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=True,   # Render Postgres typically expects SSL
    )
}

# ---------------- CORS ----------------

# IMPORTANT:
# You are using `credentials: "include"` in frontend.
# So do NOT use CORS_ALLOW_ALL_ORIGINS=True.
CORS_ALLOW_CREDENTIALS = True

# Build allowed origins list
extra_origins = [o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]

CORS_ALLOWED_ORIGINS = list(dict.fromkeys([
    *extra_origins,
    "https://electro-w3wa.onrender.com",
    "https://electromdoules-frontend.onrender.com",
    "https://electromodules.shop",
]))

# Allow required headers for Authorization + JSON
CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
    "content-type",
]

# Optional but helpful for debugging / frontend reading some headers
CORS_EXPOSE_HEADERS = ["content-type", "authorization"]

# ---------------- JWT ----------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------- Media ----------------

MEDIA_URL = "/media/"
MEDIA_ROOT = "/var/data/media"

# ---------------- Razorpay ----------------

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# ---------------- Email (SMTP) ----------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER