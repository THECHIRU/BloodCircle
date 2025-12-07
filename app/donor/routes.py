"""
Donor routes for registration, dashboard, and profile management.
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.donor import donor_bp
from app.models import Donor, User
from app.forms import DonorRegistrationForm, DonorProfileEditForm
from functools import wraps


def donor_required(f):
    """Decorator to ensure user is a donor."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'donor':
            flash('Access denied. Donors only.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@donor_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """
    Donor registration - complete profile after user registration.
    """
    # Update user role to donor if not already
    if current_user.role != 'donor':
        current_user.role = 'donor'
        db.session.commit()
    
    form = DonorRegistrationForm()
    
    # Check if user already has a donor profile
    existing_donor = current_user.donor
    
    if form.validate_on_submit():
        if existing_donor:
            # Update existing profile
            existing_donor.full_name = form.full_name.data
            existing_donor.blood_group = form.blood_group.data
            existing_donor.date_of_birth = form.date_of_birth.data
            existing_donor.gender = form.gender.data
            existing_donor.address = form.address.data
            existing_donor.city = form.city.data
            existing_donor.state = form.state.data
            existing_donor.pincode = form.pincode.data
            existing_donor.last_donation_date = form.last_donation_date.data
            existing_donor.medical_history = form.medical_history.data
            existing_donor.is_available = form.is_available.data
            existing_donor.updated_at = datetime.utcnow()
            
            flash('Donor profile updated successfully!', 'success')
        else:
            # Create new profile
            donor = Donor(
                user_id=current_user.id,
                full_name=form.full_name.data,
                blood_group=form.blood_group.data,
                date_of_birth=form.date_of_birth.data,
                gender=form.gender.data,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                pincode=form.pincode.data,
                last_donation_date=form.last_donation_date.data,
                medical_history=form.medical_history.data,
                is_available=form.is_available.data
            )
            db.session.add(donor)
            flash('Donor profile created successfully! Welcome to our community.', 'success')
        
        db.session.commit()
        
        # Notify matching patients about donor availability
        from app.utils import notify_matching_patients
        notify_matching_patients(existing_donor if existing_donor else donor)
        
        return redirect(url_for('donor.dashboard'))
    
    # Pre-fill form with existing data if available
    if request.method == 'GET' and existing_donor:
        form.full_name.data = existing_donor.full_name
        form.blood_group.data = existing_donor.blood_group
        form.date_of_birth.data = existing_donor.date_of_birth
        form.gender.data = existing_donor.gender
        form.address.data = existing_donor.address
        form.city.data = existing_donor.city
        form.state.data = existing_donor.state
        form.pincode.data = existing_donor.pincode
        form.last_donation_date.data = existing_donor.last_donation_date
        form.medical_history.data = existing_donor.medical_history
        form.is_available.data = existing_donor.is_available
    
    return render_template('donor/register.html', form=form, title='Donor Registration', existing_donor=existing_donor)


@donor_bp.route('/dashboard')
@donor_required
def dashboard():
    """Donor dashboard showing profile and statistics."""
    donor = current_user.donor
    
    if not donor:
        flash('Please complete your donor profile first.', 'warning')
        return redirect(url_for('donor.register'))
    
    # Calculate eligibility to donate
    can_donate = donor.can_donate()
    days_since_donation = None
    
    if donor.last_donation_date:
        days_since_donation = (datetime.today().date() - donor.last_donation_date).days
    
    return render_template(
        'donor/dashboard.html',
        donor=donor,
        can_donate=can_donate,
        days_since_donation=days_since_donation,
        title='Donor Dashboard'
    )


@donor_bp.route('/profile')
@donor_required
def profile():
    """View donor profile."""
    donor = current_user.donor
    
    if not donor:
        flash('Please complete your donor profile first.', 'warning')
        return redirect(url_for('donor.register'))
    
    return render_template('donor/profile.html', donor=donor, title='My Profile')


@donor_bp.route('/edit-profile', methods=['GET', 'POST'])
@donor_required
def edit_profile():
    """Edit donor profile."""
    donor = current_user.donor
    
    if not donor:
        flash('Please complete your donor profile first.', 'warning')
        return redirect(url_for('donor.register'))
    
    form = DonorProfileEditForm()
    
    if form.validate_on_submit():
        # Check if availability changed from False to True
        was_unavailable = not donor.is_available
        
        donor.full_name = form.full_name.data
        donor.address = form.address.data
        donor.city = form.city.data
        donor.state = form.state.data
        donor.pincode = form.pincode.data
        donor.last_donation_date = form.last_donation_date.data
        donor.medical_history = form.medical_history.data
        donor.is_available = form.is_available.data
        donor.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Notify patients if donor just became available
        if was_unavailable and donor.is_available:
            from app.utils import notify_matching_patients
            notify_matching_patients(donor)
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('donor.profile'))
    
    # Pre-populate form
    if request.method == 'GET':
        form.full_name.data = donor.full_name
        form.address.data = donor.address
        form.city.data = donor.city
        form.state.data = donor.state
        form.pincode.data = donor.pincode
        form.last_donation_date.data = donor.last_donation_date
        form.medical_history.data = donor.medical_history
        form.is_available.data = donor.is_available
    
    return render_template('donor/edit_profile.html', form=form, donor=donor, title='Edit Profile')


@donor_bp.route('/toggle-availability', methods=['POST'])
@donor_required
def toggle_availability():
    """Toggle donor availability status."""
    donor = current_user.donor
    
    if not donor:
        flash('Profile not found.', 'danger')
        return redirect(url_for('donor.register'))
    
    donor.is_available = not donor.is_available
    donor.updated_at = datetime.utcnow()
    db.session.commit()
    
    status = "available" if donor.is_available else "unavailable"
    flash(f'Your availability status has been updated to {status}.', 'success')
    
    return redirect(url_for('donor.dashboard'))
