"""
Utility functions for the BloodCircle application.
"""
from flask import current_app
from app import db


def format_phone_number(phone):
    """
    Format phone number to a standardized format.
    
    Args:
        phone: Phone number
    
    Returns:
        str: Formatted phone number
    """
    if not phone:
        return None
    
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Add country code if not present (assuming +1 for US)
    if not digits.startswith('1') and len(digits) == 10:
        digits = '1' + digits
    
    return '+' + digits


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates using Haversine formula.
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
    
    Returns:
        float: Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def get_blood_group_statistics():
    """
    Get statistics about blood groups in the system.
    
    Returns:
        dict: Statistics including total donors, patients, and blood group distribution
    """
    from app.models import Donor, Patient
    from sqlalchemy import func
    
    # Total counts
    total_donors = Donor.query.count()
    total_patients = Patient.query.count()
    available_donors = Donor.query.filter_by(is_available=True).count()
    
    # Blood group distribution for donors
    donor_distribution = db.session.query(
        Donor.blood_group,
        func.count(Donor.id)
    ).group_by(Donor.blood_group).all()
    
    # Blood group requests from patients
    patient_requests = db.session.query(
        Patient.blood_group_required,
        func.count(Patient.id)
    ).group_by(Patient.blood_group_required).all()
    
    return {
        'total_donors': total_donors,
        'total_patients': total_patients,
        'available_donors': available_donors,
        'donor_distribution': dict(donor_distribution),
        'patient_requests': dict(patient_requests)
    }


def notify_matching_donors(patient):
    """
    Stub function for notifying matching donors.
    Email notifications are disabled in this version.
    
    Args:
        patient: Patient object
    """
    current_app.logger.info(f"Notify donors feature called for patient {patient.id} (email disabled)")
    return True


def notify_matching_patients(donor):
    """
    Stub function for notifying matching patients.
    Email notifications are disabled in this version.
    
    Args:
        donor: Donor object
    """
    current_app.logger.info(f"Notify patients feature called for donor {donor.id} (email disabled)")
    return True
