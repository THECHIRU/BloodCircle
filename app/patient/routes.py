"""
Patient routes for registration, dashboard, and donor search.
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.patient import patient_bp
from app.models import Patient, Donor, User, get_compatible_blood_groups
from app.forms import PatientRegistrationForm, SearchDonorForm
from functools import wraps


def patient_required(f):
    """Decorator to ensure user is a patient."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'patient':
            flash('Access denied. Patients only.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@patient_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Patient registration - complete profile after user registration."""
    # Update user role to patient if not already
    if current_user.role != 'patient':
        current_user.role = 'patient'
        db.session.commit()
    
    form = PatientRegistrationForm()
    
    # Check if user already has a patient profile
    existing_patient = current_user.patient
    
    if form.validate_on_submit():
        if existing_patient:
            # Update existing profile
            existing_patient.full_name = form.full_name.data
            existing_patient.phone = form.phone.data
            existing_patient.blood_group_required = form.blood_group_required.data
            existing_patient.hospital_name = form.hospital_name.data
            existing_patient.city = form.city.data
            existing_patient.state = form.state.data
            existing_patient.pincode = form.pincode.data
            existing_patient.urgency_level = form.urgency_level.data
            existing_patient.required_by_date = form.required_by_date.data
            existing_patient.medical_condition = form.medical_condition.data
            existing_patient.updated_at = datetime.utcnow()
            
            flash('Patient profile updated successfully!', 'success')
        else:
            # Create new profile
            patient = Patient(
                user_id=current_user.id,
                full_name=form.full_name.data,
                phone=form.phone.data,
                blood_group_required=form.blood_group_required.data,
                hospital_name=form.hospital_name.data,
                city=form.city.data,
                state=form.state.data,
                pincode=form.pincode.data,
                urgency_level=form.urgency_level.data,
                required_by_date=form.required_by_date.data,
                medical_condition=form.medical_condition.data,
                is_fulfilled=False
            )
            db.session.add(patient)
            flash('Patient profile created successfully!', 'success')
        
        db.session.commit()
        
        # Notify matching donors about patient need
        from app.utils import notify_matching_donors
        notify_matching_donors(existing_patient if existing_patient else patient)
        
        return redirect(url_for('patient.dashboard'))
    
    # Pre-fill form with existing data if available
    if request.method == 'GET' and existing_patient:
        form.full_name.data = existing_patient.full_name
        form.phone.data = existing_patient.phone
        form.blood_group_required.data = existing_patient.blood_group_required
        form.hospital_name.data = existing_patient.hospital_name
        form.city.data = existing_patient.city
        form.state.data = existing_patient.state
        form.pincode.data = existing_patient.pincode
        form.urgency_level.data = existing_patient.urgency_level
        form.required_by_date.data = existing_patient.required_by_date
        form.medical_condition.data = existing_patient.medical_condition
    
    return render_template('patient/register.html', form=form, title='Patient Registration', existing_patient=existing_patient)


@patient_bp.route('/dashboard')
@patient_required
def dashboard():
    """Patient dashboard showing profile and matching donors."""
    patient = current_user.patient
    
    if not patient:
        flash('Please complete your patient profile first.', 'warning')
        return redirect(url_for('patient.register'))
    
    # Get compatible blood groups
    compatible_groups = get_compatible_blood_groups(patient.blood_group_required)
    
    # Find available donors with compatible blood groups in same city
    matching_donors = Donor.query.filter(
        Donor.blood_group.in_(compatible_groups),
        Donor.is_available == True,
        Donor.city.ilike(f'%{patient.city}%')
    ).limit(10).all()
    
    # Calculate days remaining
    days_remaining = patient.days_remaining()
    
    return render_template(
        'patient/dashboard.html',
        patient=patient,
        matching_donors=matching_donors,
        days_remaining=days_remaining,
        title='Patient Dashboard'
    )


@patient_bp.route('/search', methods=['GET', 'POST'])
@patient_required
def search_donors():
    """Search for blood donors with filters."""
    patient = current_user.patient
    
    if not patient:
        flash('Please complete your patient profile first.', 'warning')
        return redirect(url_for('patient.register'))
    
    form = SearchDonorForm()
    
    # Start with base query
    query = Donor.query
    
    # Get compatible blood groups for patient
    compatible_groups = get_compatible_blood_groups(patient.blood_group_required)
    
    # Apply filters
    if form.validate_on_submit() or request.method == 'GET':
        blood_group = request.args.get('blood_group') or (form.blood_group.data if form.blood_group.data else None)
        city = request.args.get('city') or (form.city.data if form.city.data else None)
        state = request.args.get('state') or (form.state.data if form.state.data else None)
        available_only = request.args.get('available_only', 'true').lower() == 'true'
        
        if blood_group:
            query = query.filter(Donor.blood_group == blood_group)
        else:
            # Show only compatible blood groups
            query = query.filter(Donor.blood_group.in_(compatible_groups))
        
        if city:
            query = query.filter(Donor.city.ilike(f'%{city}%'))
        
        if state:
            query = query.filter(Donor.state.ilike(f'%{state}%'))
        
        if available_only:
            query = query.filter(Donor.is_available == True)
    else:
        # Default: show compatible blood groups in same city
        query = query.filter(
            Donor.blood_group.in_(compatible_groups),
            Donor.city.ilike(f'%{patient.city}%')
        )
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    donors = pagination.items
    
    return render_template(
        'patient/search_donors.html',
        form=form,
        donors=donors,
        pagination=pagination,
        patient=patient,
        compatible_groups=compatible_groups,
        title='Search Donors'
    )


@patient_bp.route('/donor/<int:donor_id>')
@patient_required
def view_donor(donor_id):
    """View detailed donor information."""
    patient = current_user.patient
    
    if not patient:
        flash('Please complete your patient profile first.', 'warning')
        return redirect(url_for('patient.register'))
    
    donor = Donor.query.get_or_404(donor_id)
    
    # Check if donor's blood group is compatible
    compatible_groups = get_compatible_blood_groups(patient.blood_group_required)
    is_compatible = donor.blood_group in compatible_groups
    
    return render_template(
        'patient/view_donor.html',
        donor=donor,
        patient=patient,
        is_compatible=is_compatible,
        now=datetime.now(),
        title=f'Donor - {donor.full_name}'
    )


@patient_bp.route('/profile')
@patient_required
def profile():
    """View patient profile."""
    patient = current_user.patient
    
    if not patient:
        flash('Please complete your patient profile first.', 'warning')
        return redirect(url_for('patient.register'))
    
    days_remaining = patient.days_remaining()
    compatible_groups = get_compatible_blood_groups(patient.blood_group_required)
    
    return render_template(
        'patient/profile.html',
        patient=patient,
        days_remaining=days_remaining,
        compatible_groups=compatible_groups,
        title='My Profile'
    )
