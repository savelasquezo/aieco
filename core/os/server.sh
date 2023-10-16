#!/bin/bash
DJANGODIR=$(dirname $(cd `dirname $0` && pwd))
DJANGO_SETTINGS_MODULE=core.settings
cd $DJANGODIR
source /home/app/venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
exec python3 manage.py runserver 5.183.9.247


