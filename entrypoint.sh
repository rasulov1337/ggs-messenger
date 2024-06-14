#!/bin/bash

set -e

echo "${0}: running migrations."
# python manage.py makemigrations --merge
python manage.py migrate --noinput

echo "${0}: collecting statics."
python manage.py collectstatic --noinput

# cp -rv static/* static_shared/

# gunicorn yourapp.wsgi:application \
    # --env DJANGO_SETTINGS_MODULE=yourapp.production_settings \
    # --reload  # Only for development
# python manage.py runserver 0.0.0.0:8000
gunicorn -c /app/gunicorn.conf.py msgr.wsgi