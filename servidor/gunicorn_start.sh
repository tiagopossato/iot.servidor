#!/bin/bash

NAME="servidor"                              #Name of the application (*)  
DJANGODIR=/opt/iot.servidor/servidor             # Django project directory (*)  
USER=servidor                                       # the user to run as (*)  
#GROUP=debian                                     # the group to run as (*)  
NUM_WORKERS=1                                     # how many worker processes should Gunicorn spawn (*)  
DJANGO_SETTINGS_MODULE=servidor.settings             # which settings file should Django use (*)  
DJANGO_WSGI_MODULE=servidor.wsgi                     # WSGI module name (*)

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR  
source /etc/profile
workon centralvenv

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE  
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
killall gunicorn
gunicorn ${DJANGO_WSGI_MODULE}:application --name $NAME --workers $NUM_WORKERS --user $USER --bind 127.0.0.1:8000 --bind [::1]:8000 --log-level debug