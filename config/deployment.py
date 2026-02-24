import os
from pathlib import Path
import dj_database_url
from datetime import timedelta
from .settings import *
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------- SECURITY ----------------

DEBUG = True

SECRET_KEY = os.getenv("SECRET_KEY")

ALLOWED_HOSTS = list(filter(None, [
    os.environ.get('RENDER_EXTERNAL_HOSTNAME'),
]))

CSRF_TRUSTED_ORIGINS = [
    "https://" + os.environ.get("RENDER_EXTERNAL_HOSTNAME"),
    "https://electromdoules-frontend.onrender.com",
    "https://electromodules.shop",
]

# ---------------- Razorpay ----------------

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# ---------------- Middleware ----------------

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ---------------- Static files ----------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# ---------------- Database ----------------

DATABASES = {
    'default': dj_database_url.config(
        default= os.environ['DATABASE_URL'], 
        conn_max_age=600
    )
}

# ---------------- CORS ----------------

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = list(filter(None, [
    *os.getenv("CORS_ALLOWED_ORIGINS", "").split(","),
    "https://electromdoules-frontend.onrender.com",
    "https://electromodules.shop",
]))

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
    "content-type",
]
# ---------------- JWT ----------------

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = "/var/data/media"
# ---------------- Email (SMTP) ----------------

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
