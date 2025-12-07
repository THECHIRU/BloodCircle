#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# CRITICAL: Fix database phone column DIRECTLY
echo "=== FIXING DATABASE PHONE COLUMN ==="
python fix_phone_direct.py

# Initialize and update schema
echo "=== INITIALIZING DATABASE ==="
python init_db.py
