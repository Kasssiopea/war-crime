#!/bin/bash
echo "Collect static files"
python manage.py collectstatic --noinput --clear
python manage.py compilemessages
echo "Apply database migrations"
python manage.py migrate
echo "Starting server (Production)"
gunicorn --bind 0.0.0.0:8000 DRF_DIAP.wsgi:application