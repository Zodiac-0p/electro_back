import os
from pathlib import Path
from datetime import timedelta

import dj_database_url
from corsheaders.defaults import default_headers, default_methods

# ✅ IMPORTANT: import your base settings
from .settings import *  # noqa

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------- SECURITY ----------------
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", SECRET_KEY)

RENDER_HOST = os.getenv("RENDER_EXTERNAL_HOSTNAME")

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# ✅ Render assigned hostname
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)

# ✅ Add your Render service domains explicitly (helps when RENDER_HOST changes)
ALLOWED_HOSTS += [
    "electro-back-5.onrender.com",
    "electro-backend-f1rh.onrender.com",
]

# Optional custom domain
CUSTOM_DOMAIN = os.getenv("CUSTOM_DOMAIN")
if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)

# ✅ Render/Cloudflare proxy header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# ---------------- Middleware ----------------
# Recommended: Security -> CORS -> WhiteNoise -> Session -> Common -> CSRF...
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
# ✅ You are using JWT (Authorization header). No cookies needed.
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_ALL_ORIGINS = False

extra_origins = [
    o.strip()
    for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if o.strip()
]

CORS_ALLOWED_ORIGINS = list(dict.fromkeys([
    # env first (optional)
    *extra_origins,

    # ✅ your current frontend
    "https://electro-w3wa.onrender.com",

    # old/optional frontends
    "https://electromdoules-frontend.onrender.com",
    "https://electromodules.shop",

    # local dev
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]))

# ✅ Preflight support
CORS_ALLOW_METHODS = list(default_methods)

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
    "content-type",
]

# (optional) expose headers
CORS_EXPOSE_HEADERS = ["Content-Type", "Authorization"]


# ---------------- CSRF ----------------
# ✅ Only needed if you use cookie-based auth / sessions.
CSRF_TRUSTED_ORIGINS = [
    "https://electro-w3wa.onrender.com",
    "https://electromdoules-frontend.onrender.com",
    "https://electromodules.shop",
]
if RENDER_HOST:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_HOST}")


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