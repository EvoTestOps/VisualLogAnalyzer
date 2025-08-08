#!/bin/bash

set -e

echo "Running db migrations..."
flask --app main.py db upgrade

echo "Starting application with command $APP_CMD"
exec $APP_CMD
