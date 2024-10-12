#!/bin/sh

export DJANGO_SETTINGS_MODULE=app.settings

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z ${POSTGRES_HOST} 5432; do   
  sleep 1
done

# Migrate server
echo "/!\\   DEBUG: python manage.py migrate   /!\\"
python manage.py makemigrations
python manage.py migrate

# Create SUPERUSER
echo "/!\\   DEBUG: Create SUPERUSER   /!\\" 
cat << EOF > tools/create_superuser.py
from django.contrib.auth import get_user_model

User = get_user_model()
username = '${SUPERUSER_USERNAME}'
email = '${SUPERUSER_EMAIL}'
password = '${SUPERUSER_PASSWORD}'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superuser {username} created.')
else:
    print('Superuser already exists.')
EOF

python manage.py shell < tools/create_superuser.py
rm -f tools/create_superuser.py

# Launch server
echo "/!\\   DEBUG: python manage.py runserver 0.0.0.0:8000   /!\\"
exec "$@"
