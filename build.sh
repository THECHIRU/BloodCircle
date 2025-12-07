#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# FORCE fix database schema issues FIRST
python force_fix_db.py

# Then run the regular fix
python fix_database.py

# Initialize the database
python init_db.py
