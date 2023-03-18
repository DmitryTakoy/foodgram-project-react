#!/bin/sh

python manage.py makemigrations core
python manage.py migrate core
python manage.py makemigrations api
python manage.py migrate api
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
exec "$@"