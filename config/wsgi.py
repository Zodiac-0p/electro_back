import os
from django.core.wsgi import get_wsgi_application

# ✅ If DJANGO_SETTINGS_MODULE is set in Render env, use it
# otherwise fallback to deployment on Render
if not os.getenv("DJANGO_SETTINGS_MODULE"):
    settings_module = "config.deployment" if os.getenv("RENDER_EXTERNAL_HOSTNAME") else "config.settings"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

application = get_wsgi_application()