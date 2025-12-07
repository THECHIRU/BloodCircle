#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Initialize database with clean schema
python init_db_clean.py
