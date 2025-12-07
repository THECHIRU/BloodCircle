"""
Patient blueprint initialization.
"""
from flask import Blueprint

patient_bp = Blueprint('patient', __name__)

from app.patient import routes
