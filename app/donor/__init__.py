"""
Donor blueprint initialization.
"""
from flask import Blueprint

donor_bp = Blueprint('donor', __name__)

from app.donor import routes
