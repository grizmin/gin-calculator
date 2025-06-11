#!/bin/sh

echo "🍸 Starting Gin Calculator setup..."

# Create volume directories if they don't exist
mkdir -p /app/db_data
mkdir -p /app/media
mkdir -p /app/staticfiles

# Set proper permissions
chown -R gin_user:gin_user /app/db_data /app/media /app/staticfiles 2>/dev/null || true

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create admin user if it doesn't exist
echo "Setting up admin user..."
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gin_calculator.settings')
django.setup()

from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Admin user created: admin/admin123')
else:
    print('ℹ️ Admin user already exists')
"

# Create default recipe
echo "Setting up default recipe..."
python manage.py create_default_recipe

echo "🚀 Starting server..."
exec python manage.py runserver 0.0.0.0:8000
