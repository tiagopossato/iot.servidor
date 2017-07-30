#!/bin/bash

NAME="servidor"                              #Name of the application (*)  
DJANGODIR=/home/debian/iot.servidor/servidor             # Django project directory (*)  
SOCKFILE=/home/debian/iot.servidor/servidor/run/gunicorn.sock        # we will communicate using this unix socket (*)  
USER=servidor                                       # the user to run as (*)  
#GROUP=debian                                     # the group to run as (*)  
NUM_WORKERS=1                                     # how many worker processes should Gunicorn spawn (*)  
DJANGO_SETTINGS_MODULE=servidor.settings             # which settings file should Django use (*)  
DJANGO_WSGI_MODULE=servidor.wsgi                     # WSGI module name (*)

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR  
source /home/debian/.virtualenvs/servidor/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE  
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)  
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
/home/debian/.virtualenvs/servidor/bin/gunicorn ${DJANGO_WSGI_MODULE}:application --name $NAME --workers $NUM_WORKERS --user $USER --bind 127.0.0.1:8000 --bind [::1]:8000
#--bind=unix:$SOCKFILE