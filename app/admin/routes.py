"""
Admin routes for dashboard, user management, and CRUD operations.
"""
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.admin import admin_bp
from app.models import User, Donor, Patient, Feedback
from app.forms import AdminFeedbackResponseForm, AdminEditUserForm
from app.utils import get_blood_group_statistics
from functools import wraps


def admin_required(f):
    """Decorator to ensure user is an admin."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admins only.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with statistics and overview."""
    # Get statistics
    stats = get_blood_group_statistics()
    
    # Recent users (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_users = User.query.filter(User.created_at >= week_ago).count()
    
    # Total users by role
    total_admins = User.query.filter_by(role='admin').count()
    total_donors = User.query.filter_by(role='donor').count()
    total_patients = User.query.filter_by(role='patient').count()
    
    # Pending feedback
    pending_feedback = Feedback.query.filter_by(is_resolved=False).count()
    
    # Recent feedback
    recent_feedback = Feedback.query.order_by(Feedback.created_at.desc()).limit(5).all()
    
    # Urgent patient requests
    urgent_patients = Patient.query.filter(
        Patient.urgency_level == 'Critical',
        Patient.is_fulfilled == False
    ).limit(5).all()
    
    # Blood group distribution data for charts
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    donor_counts = []
    patient_counts = []
    
    for bg in blood_groups:
        donor_counts.append(stats['donor_distribution'].get(bg, 0))
        patient_counts.append(stats['patient_requests'].get(bg, 0))
    
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_users=recent_users,
        total_admins=total_admins,
        total_donors=total_donors,
        total_patients=total_patients,
        pending_feedback=pending_feedback,
        recent_feedback=recent_feedback,
        urgent_patients=urgent_patients,
        blood_groups=blood_groups,
        donor_counts=donor_counts,
        patient_counts=patient_counts,
        title='Admin Dashboard'
    )


@admin_bp.route('/users')
@admin_required
def manage_users():
    """Manage all users."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filter options
    role_filter = request.args.get('role', 'all')
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '')
    
    query = User.query
    
    # Apply filters
    if role_filter != 'all':
        query = query.filter_by(role=role_filter)
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    elif status_filter == 'unverified':
        query = query.filter_by(is_verified=False)
    
    if search_query:
        search_filters = [User.email.ilike(f'%{search_query}%')]
        # Only search phone if it's not null
        search_filters.append(User.phone.ilike(f'%{search_query}%'))
        # Exact ID match if search query is a number
        if search_query.isdigit():
            search_filters.append(User.id == int(search_query))
        query = query.filter(db.or_(*search_filters))
    
    # Order by creation date (newest first)
    query = query.order_by(User.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    return render_template(
        'admin/manage_users.html',
        users=users,
        pagination=pagination,
        role_filter=role_filter,
        status_filter=status_filter,
        search_query=search_query,
        title='Manage Users'
    )


@admin_bp.route('/donors')
@admin_required
def manage_donors():
    """Manage donors."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filter options
    blood_group_filter = request.args.get('blood_group', 'all')
    availability_filter = request.args.get('availability', 'all')
    city_filter = request.args.get('city', '')
    search_query = request.args.get('search', '')
    
    query = Donor.query
    
    # Apply filters
    if blood_group_filter != 'all':
        query = query.filter_by(blood_group=blood_group_filter)
    
    if availability_filter == 'available':
        query = query.filter_by(is_available=True)
    elif availability_filter == 'unavailable':
        query = query.filter_by(is_available=False)
    
    if city_filter:
        query = query.filter(Donor.city.ilike(f'%{city_filter}%'))
    
    # Search functionality
    if search_query:
        search_filters = [
            Donor.full_name.ilike(f'%{search_query}%'),
            Donor.phone.ilike(f'%{search_query}%')
        ]
        # Exact ID match if search query is a number
        if search_query.isdigit():
            search_filters.append(Donor.id == int(search_query))
        query = query.filter(db.or_(*search_filters))
    
    # Order by creation date (newest first)
    query = query.order_by(Donor.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    donors = pagination.items
    
    # Get unique cities for filter
    cities = db.session.query(Donor.city).distinct().all()
    cities = [city[0] for city in cities]
    
    return render_template(
        'admin/manage_donors.html',
        donors=donors,
        pagination=pagination,
        blood_group_filter=blood_group_filter,
        availability_filter=availability_filter,
        city_filter=city_filter,
        cities=cities,
        search_query=search_query,
        title='Manage Donors'
    )


@admin_bp.route('/patients')
@admin_required
def manage_patients():
    """Manage patients."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filter options
    blood_group_filter = request.args.get('blood_group', 'all')
    urgency_filter = request.args.get('urgency', 'all')
    fulfillment_filter = request.args.get('fulfillment', 'all')
    search_query = request.args.get('search', '')
    
    query = Patient.query
    
    # Apply filters
    if blood_group_filter != 'all':
        query = query.filter_by(blood_group_required=blood_group_filter)
    
    if urgency_filter != 'all':
        query = query.filter_by(urgency_level=urgency_filter)
    
    if fulfillment_filter == 'fulfilled':
        query = query.filter_by(is_fulfilled=True)
    elif fulfillment_filter == 'pending':
        query = query.filter_by(is_fulfilled=False)
    
    # Search functionality
    if search_query:
        search_filters = [
            Patient.full_name.ilike(f'%{search_query}%'),
            Patient.phone.ilike(f'%{search_query}%')
        ]
        # Exact ID match if search query is a number
        if search_query.isdigit():
            search_filters.append(Patient.id == int(search_query))
        query = query.filter(db.or_(*search_filters))
    
    # Order by urgency and creation date
    query = query.order_by(Patient.urgency_level, Patient.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    patients = pagination.items
    
    return render_template(
        'admin/manage_patients.html',
        patients=patients,
        pagination=pagination,
        blood_group_filter=blood_group_filter,
        urgency_filter=urgency_filter,
        fulfillment_filter=fulfillment_filter,
        search_query=search_query,
        title='Manage Patients'
    )


@admin_bp.route('/feedback')
@admin_required
def manage_feedback():
    """Manage feedback submissions."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filter options
    status_filter = request.args.get('status', 'all')
    
    query = Feedback.query
    
    # Apply filters
    if status_filter == 'pending':
        query = query.filter_by(is_resolved=False)
    elif status_filter == 'resolved':
        query = query.filter_by(is_resolved=True)
    
    # Order by creation date (newest first)
    query = query.order_by(Feedback.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    feedback_items = pagination.items
    
    return render_template(
        'admin/manage_feedback.html',
        feedback_items=feedback_items,
        pagination=pagination,
        status_filter=status_filter,
        title='Manage Feedback'
    )


@admin_bp.route('/user/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Activate or deactivate a user."""
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin' and user.id != current_user.id:
        # Prevent deactivating other admins
        flash('Cannot modify other admin accounts.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = "activated" if user.is_active else "deactivated"
    flash(f'User {user.email} has been {status}.', 'success')
    
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user (admin only) - soft delete with 24h grace period."""
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin':
        flash('Cannot delete admin accounts.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    if user.id == current_user.id:
        flash('Cannot delete your own account.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # Soft delete - set deleted_at timestamp
    email = user.email
    user.deleted_at = datetime.utcnow()
    user.is_active = False
    if user.donor:
        user.donor.is_available = False
    
    db.session.commit()
    
    flash(f'User {email} has been deleted. They can re-register after 24 hours.', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/feedback/<int:feedback_id>/respond', methods=['GET', 'POST'])
@admin_required
def respond_feedback(feedback_id):
    """Respond to feedback."""
    feedback = Feedback.query.get_or_404(feedback_id)
    form = AdminFeedbackResponseForm()
    
    if form.validate_on_submit():
        feedback.admin_response = form.admin_response.data
        feedback.is_resolved = True
        feedback.resolved_at = datetime.utcnow()
        db.session.commit()
        
        # Email notification disabled (response saved in database)
        current_app.logger.info(f"Feedback {feedback.id} responded to: {feedback.email}")
        
        flash('Response sent successfully!', 'success')
        return redirect(url_for('admin.manage_feedback'))
    
    return render_template(
        'admin/respond_feedback.html',
        feedback=feedback,
        form=form,
        title='Respond to Feedback'
    )


@admin_bp.route('/feedback/<int:feedback_id>/resolve', methods=['POST'])
@admin_required
def resolve_feedback(feedback_id):
    """Mark feedback as resolved without response."""
    feedback = Feedback.query.get_or_404(feedback_id)
    
    feedback.is_resolved = True
    feedback.resolved_at = datetime.utcnow()
    db.session.commit()
    
    flash('Feedback marked as resolved.', 'success')
    return redirect(url_for('admin.manage_feedback'))


@admin_bp.route('/feedback/<int:feedback_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_feedback_status(feedback_id):
    """Toggle feedback resolved status."""
    feedback = Feedback.query.get_or_404(feedback_id)
    
    feedback.is_resolved = not feedback.is_resolved
    if feedback.is_resolved:
        feedback.resolved_at = datetime.utcnow()
    else:
        feedback.resolved_at = None
    
    db.session.commit()
    
    status = "resolved" if feedback.is_resolved else "pending"
    flash(f'Feedback marked as {status}.', 'success')
    return redirect(url_for('admin.manage_feedback'))


@admin_bp.route('/patient/<int:patient_id>/fulfill', methods=['POST'])
@admin_required
def fulfill_patient_request(patient_id):
    """Mark patient request as fulfilled."""
    patient = Patient.query.get_or_404(patient_id)
    
    patient.is_fulfilled = True
    patient.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Request for {patient.full_name} marked as fulfilled.', 'success')
    return redirect(url_for('admin.manage_patients'))


@admin_bp.route('/stats/export')
@admin_required
def export_stats():
    """Export statistics as CSV."""
    import csv
    from io import StringIO
    from flask import make_response
    
    # Get statistics
    stats = get_blood_group_statistics()
    
    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    
    # Write headers
    writer.writerow(['Blood Group', 'Donors', 'Patient Requests'])
    
    # Write data
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    for bg in blood_groups:
        writer.writerow([
            bg,
            stats['donor_distribution'].get(bg, 0),
            stats['patient_requests'].get(bg, 0)
        ])
    
    # Create response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=blood_donation_stats.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output


@admin_bp.route('/block-user/<int:user_id>', methods=['POST'])
@login_required
def block_user(user_id):
    """Block a user from accessing the platform."""
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin':
        flash('Cannot block admin users.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user.is_blocked = True
    user.is_active = False
    db.session.commit()
    
    flash(f'User {user.email} has been blocked successfully.', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/unblock-user/<int:user_id>', methods=['POST'])
@login_required
def unblock_user(user_id):
    """Unblock a user."""
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    user.is_blocked = False
    user.is_active = True
    db.session.commit()
    
    flash(f'User {user.email} has been unblocked successfully.', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit user data."""
    user = User.query.get_or_404(user_id)
    form = AdminEditUserForm()
    
    if form.validate_on_submit():
        user.email = form.email.data
        user.phone = form.phone.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        user.is_verified = form.is_verified.data
        user.is_blocked = form.is_blocked.data
        
        # Update donor data if exists
        if user.donor:
            if form.donor_full_name.data:
                user.donor.full_name = form.donor_full_name.data
            if form.donor_phone.data:
                user.donor.phone = form.donor_phone.data
            if form.donor_blood_group.data:
                user.donor.blood_group = form.donor_blood_group.data
            if form.donor_city.data:
                user.donor.city = form.donor_city.data
            if form.donor_state.data:
                user.donor.state = form.donor_state.data
            if form.donor_pincode.data:
                user.donor.pincode = form.donor_pincode.data
                
        # Update patient data if exists
        if user.patient:
            if form.patient_full_name.data:
                user.patient.full_name = form.patient_full_name.data
            if form.patient_phone.data:
                user.patient.phone = form.patient_phone.data
            if form.patient_blood_group_required.data:
                user.patient.blood_group_required = form.patient_blood_group_required.data
            if form.patient_hospital.data:
                user.patient.hospital_name = form.patient_hospital.data
            if form.patient_city.data:
                user.patient.city = form.patient_city.data
            if form.patient_state.data:
                user.patient.state = form.patient_state.data
            if form.patient_pincode.data:
                user.patient.pincode = form.patient_pincode.data
        
        db.session.commit()
        flash(f'User {user.email} updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    # Pre-populate form
    if request.method == 'GET':
        form.email.data = user.email
        form.phone.data = user.phone
        form.role.data = user.role
        form.is_active.data = user.is_active
        form.is_verified.data = user.is_verified
        form.is_blocked.data = user.is_blocked
        
        # Pre-populate donor fields
        if user.donor:
            form.donor_full_name.data = user.donor.full_name
            form.donor_phone.data = user.donor.phone
            form.donor_blood_group.data = user.donor.blood_group
            form.donor_city.data = user.donor.city
            form.donor_state.data = user.donor.state
            form.donor_pincode.data = user.donor.pincode
            
        # Pre-populate patient fields
        if user.patient:
            form.patient_full_name.data = user.patient.full_name
            form.patient_phone.data = user.patient.phone
            form.patient_blood_group_required.data = user.patient.blood_group_required
            form.patient_hospital.data = user.patient.hospital_name
            form.patient_city.data = user.patient.city
            form.patient_state.data = user.patient.state
            form.patient_pincode.data = user.patient.pincode
    
    return render_template('admin/edit_user.html', form=form, user=user, title='Edit User')


@admin_bp.route('/sub-admin/dashboard')
@login_required
def sub_admin_dashboard():
    """Sub-admin dashboard - view only access."""
    if current_user.role != 'sub_admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get statistics (same as admin dashboard but read-only)
    total_users = User.query.count()
    total_donors = Donor.query.count()
    total_patients = Patient.query.count()
    active_donors = Donor.query.filter_by(is_available=True).count()
    
    # Get recent registrations
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_donors = Donor.query.order_by(Donor.created_at.desc()).limit(5).all()
    
    return render_template('admin/sub_admin_dashboard.html',
                         total_users=total_users,
                         total_donors=total_donors,
                         total_patients=total_patients,
                         active_donors=active_donors,
                         recent_users=recent_users,
                         recent_donors=recent_donors,
                         title='Sub-Admin Dashboard')


@admin_bp.route('/sub-admin/users')
@login_required
def sub_admin_users():
    """View all users (read-only)."""
    if current_user.role != 'sub_admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/sub_admin_users.html', users=users, title='View Users')


@admin_bp.route('/sub-admin/donors')
@login_required
def sub_admin_donors():
    """View all donors (read-only)."""
    if current_user.role != 'sub_admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    donors = Donor.query.order_by(Donor.created_at.desc()).all()
    return render_template('admin/sub_admin_donors.html', donors=donors, title='View Donors')


@admin_bp.route('/sub-admin/patients')
@login_required
def sub_admin_patients():
    """View all patients (read-only)."""
    if current_user.role != 'sub_admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return render_template('admin/sub_admin_patients.html', patients=patients, title='View Patients')
