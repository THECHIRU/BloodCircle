#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Fix database schema issues
python fix_database.py

# Initialize the database
python init_db.py
