"""
Role switching functionality - allows users to switch between donor and patient roles.
"""
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.main import main_bp


@main_bp.route('/switch-to-patient')
@login_required
def switch_to_patient():
    """Switch from donor to patient role."""
    if current_user.role == 'admin' or current_user.role == 'sub_admin':
        flash('Admins cannot switch to patient role.', 'danger')
        return redirect(url_for('main.index'))
    
    if current_user.role == 'patient':
        flash('You are already registered as a patient.', 'info')
        return redirect(url_for('patient.dashboard'))
    
    # If user has existing patient profile, just switch role
    if current_user.patient:
        current_user.role = 'patient'
        db.session.commit()
        flash('Switched to patient profile successfully!', 'success')
        return redirect(url_for('patient.dashboard'))
    
    # Otherwise, switch role and redirect to patient registration
    current_user.role = 'patient'
    db.session.commit()
    flash('Please complete your patient profile.', 'info')
    return redirect(url_for('patient.register'))


@main_bp.route('/switch-to-donor')
@login_required
def switch_to_donor():
    """Switch from patient to donor role."""
    if current_user.role == 'admin' or current_user.role == 'sub_admin':
        flash('Admins cannot switch to donor role.', 'danger')
        return redirect(url_for('main.index'))
    
    if current_user.role == 'donor':
        flash('You are already registered as a donor.', 'info')
        return redirect(url_for('donor.dashboard'))
    
    # If user has existing donor profile, just switch role
    if current_user.donor:
        current_user.role = 'donor'
        db.session.commit()
        flash('Switched to donor profile successfully!', 'success')
        return redirect(url_for('donor.dashboard'))
    
    # Otherwise, switch role and redirect to donor registration
    current_user.role = 'donor'
    db.session.commit()
    flash('Please complete your donor profile.', 'info')
    return redirect(url_for('donor.register'))
