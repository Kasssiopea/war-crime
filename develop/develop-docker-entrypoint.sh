#!/bin/bash
echo "Apply database migrations"
python manage.py migrate
python manage.py compilemessages
echo "Starting server (Production)"
python /code/manage.py runserver 0.0.0.0:8000