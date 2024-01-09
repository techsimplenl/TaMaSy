#!/bin/sh

if [ "$DATABASE" == "adminDB" ]
then
    echo "Waiting for postgres..."
    echo $POSTGRES_HOST
    echo $POSTGRES_PORT
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python3 manage.py makemigrations --noinput --settings=admin.settings.deployment
python3 manage.py migrate --noinput --settings=admin.settings.deployment
python3 manage.py collectstatic --settings=admin.settings.deployment
# python3 manage.py collectstatic --noinput

gunicorn --env DJANGO_SETTINGS_MODULE=admin.settings.deployment admin.wsgi:application  --bind 0.0.0.0:8000