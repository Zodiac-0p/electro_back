#!/usr/bin/env bash
set -o errexit

echo "Installing dependencies..."
pip install --only-binary=:all: -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

if [ "$CREATE_SUPERUSER" = "true" ]; then
  echo "Creating superuser if not exists..."

  python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if username and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print("Superuser created")
    else:
        print("Superuser already exists")
else:
    print("Superuser env vars not set — skipping creation")
EOF

fi

echo "Build finished successfully."
