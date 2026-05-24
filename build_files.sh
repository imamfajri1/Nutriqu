#!/bin/bash
pip install --break-system-packages -r requirements.txt
python manage.py migrate --settings=config.settings.production
python manage.py import_foods --settings=config.settings.production
python manage.py collectstatic --noinput --settings=config.settings.production
