#!/bin/bash
# Скрипт для инициализации базы данных

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

