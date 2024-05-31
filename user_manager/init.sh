#!/bin/bash

python3 manage.py makemigrations user_manager

python3 manage.py migrate user_manager

python3 manage.py runserver 0.0.0.0:8080