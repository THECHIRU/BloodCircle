#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running database migration..."
python migrate_phone_fields.py

echo "Initializing database..."
python init_admin.py

echo "Build completed successfully!"
