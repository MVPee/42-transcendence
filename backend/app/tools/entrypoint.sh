#!/bin/bash

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

# Define superuser details in arrays
USERNAMES=("$SUPERUSER_USERNAME" "$SUPERUSER1_USERNAME" "$SUPERUSER2_USERNAME" "$SUPERUSER3_USERNAME")
EMAILS=("$SUPERUSER_EMAIL" "$SUPERUSER1_EMAIL" "$SUPERUSER2_EMAIL" "$SUPERUSER3_EMAIL")
PASSWORDS=("$SUPERUSER_PASSWORD" "$SUPERUSER1_PASSWORD" "$SUPERUSER2_PASSWORD" "$SUPERUSER3_PASSWORD")

for i in 0 1 2 3; do
    username=${USERNAMES[$i]}
    email=${EMAILS[$i]}
    password=${PASSWORDS[$i]}

    # Only proceed if the username is not empty
    if [ -n "$username" ]; then
        cat << EOF > tools/create_superuser.py
from django.contrib.auth import get_user_model

User = get_user_model()
username = '${username}'
email = '${email}'
password = '${password}'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superuser {username} created.')
else:
    print('Superuser already exists.')
EOF

        python manage.py shell < tools/create_superuser.py
    else
        echo "Skipping SUPERUSER${i} as the username is not set."
    fi
done

# Clean up the script
rm -f tools/create_superuser.py

# Launch server
echo "/!\\   DEBUG: python manage.py runserver 0.0.0.0:8000   /!\\" 
exec "$@"
