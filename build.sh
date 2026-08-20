#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

python manage.py populate_data
python manage.py shell -c "

from django.contrib.auth import get_user_model

User = get_user_model()

username = '$ADMIN_USERNAME'
email = '$ADMIN_EMAIL'
password = '$ADMIN_PASSWORD'

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )

    if hasattr(user, 'role'):
        user.role = 'admin'
        user.save(update_fields=['role'])

    print('Admin account created successfully.')
else:
    print('Admin account already exists.')
"
