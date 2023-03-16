#!/bin/sh

python manage.py makemigrations users
python manage.py migrate users
python manage.py makemigrations fgapi
python manage.py migrate fgapi
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
exec "$@"