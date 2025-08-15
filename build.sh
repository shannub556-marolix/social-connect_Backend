#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Checking directory structure..."
ls -la

echo "Navigating to socialconnect directory..."
cd socialconnect

echo "Running Django commands..."
python manage.py collectstatic --no-input
python manage.py migrate

echo "Build completed successfully!"
