"""
Main routes for homepage, about, contact, and feedback.
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app import db
from app.main import main_bp
from app.models import Feedback, Donor, Patient, User, OTP
from app.forms import FeedbackForm


@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Homepage."""
    # Get some statistics for display
    total_donors = Donor.query.count()
    available_donors = Donor.query.filter_by(is_available=True).count()
    total_patients = Patient.query.count()
    
    # Get blood group distribution
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    
    return render_template(
        'main/index.html',
        total_donors=total_donors,
        available_donors=available_donors,
        total_patients=total_patients,
        blood_groups=blood_groups,
        title='Home - Save Lives Through Blood Donation'
    )


@main_bp.route('/about')
def about():
    """About page."""
    return render_template('main/about.html', title='About Us')


@main_bp.route('/contact')
def contact():
    """Contact page."""
    return render_template('main/contact.html', title='Contact Us')


@main_bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Feedback form page."""
    form = FeedbackForm()
    
    # Pre-fill form if user is logged in
    if current_user.is_authenticated and request.method == 'GET':
        form.email.data = current_user.email
        if current_user.donor:
            form.name.data = current_user.donor.full_name
        elif current_user.patient:
            form.name.data = current_user.patient.full_name
    
    if form.validate_on_submit():
        feedback_entry = Feedback(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data,
            rating=int(form.rating.data) if form.rating.data else None,
            is_resolved=False
        )
        
        db.session.add(feedback_entry)
        db.session.commit()
        
        flash('Thank you for your feedback! We will get back to you soon.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('main/feedback.html', form=form, title='Feedback')


@main_bp.route('/how-it-works')
def how_it_works():
    """How it works page."""
    return render_template('main/how_it_works.html', title='How It Works')


@main_bp.route('/faq')
def faq():
    """Frequently Asked Questions page."""
    faqs = [
        {
            'question': 'Who can donate blood?',
            'answer': 'Anyone between 18-65 years of age, weighing at least 50 kg, and in good health can donate blood.'
        },
        {
            'question': 'How often can I donate blood?',
            'answer': 'You can donate blood every 3 months (90 days). Our system tracks your last donation date automatically.'
        },
        {
            'question': 'Is blood donation safe?',
            'answer': 'Yes, blood donation is completely safe. Sterile, single-use equipment is used for each donation.'
        },
        {
            'question': 'How long does the donation process take?',
            'answer': 'The actual donation takes about 10-15 minutes, but the entire process including registration and refreshments takes about 45 minutes.'
        },
        {
            'question': 'What blood types are compatible?',
            'answer': 'O- is the universal donor (can donate to all blood types). AB+ is the universal recipient (can receive from all blood types). Our system automatically shows you compatible donors/patients.'
        },
        {
            'question': 'How do I search for blood donors?',
            'answer': 'After registering as a patient, you can search for donors by blood type, location, and availability. Contact information is provided for available donors.'
        },
        {
            'question': 'How is my data protected?',
            'answer': 'We use industry-standard security measures including password hashing, CSRF protection, and secure session management to protect your data.'
        },
        {
            'question': 'Can I update my availability status?',
            'answer': 'Yes! Donors can toggle their availability status anytime from their dashboard.'
        }
    ]
    
    return render_template('main/faq.html', faqs=faqs, title='FAQ')


@main_bp.route('/blood-compatibility')
def blood_compatibility():
    """Blood compatibility information page."""
    compatibility_data = {
        'O-': {
            'can_donate_to': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
            'can_receive_from': ['O-'],
            'description': 'Universal Donor'
        },
        'O+': {
            'can_donate_to': ['O+', 'A+', 'B+', 'AB+'],
            'can_receive_from': ['O-', 'O+'],
            'description': 'Common Blood Type'
        },
        'A-': {
            'can_donate_to': ['A-', 'A+', 'AB-', 'AB+'],
            'can_receive_from': ['A-', 'O-'],
            'description': 'Rare Blood Type'
        },
        'A+': {
            'can_donate_to': ['A+', 'AB+'],
            'can_receive_from': ['A-', 'A+', 'O-', 'O+'],
            'description': 'Common Blood Type'
        },
        'B-': {
            'can_donate_to': ['B-', 'B+', 'AB-', 'AB+'],
            'can_receive_from': ['B-', 'O-'],
            'description': 'Rare Blood Type'
        },
        'B+': {
            'can_donate_to': ['B+', 'AB+'],
            'can_receive_from': ['B-', 'B+', 'O-', 'O+'],
            'description': 'Common Blood Type'
        },
        'AB-': {
            'can_donate_to': ['AB-', 'AB+'],
            'can_receive_from': ['AB-', 'A-', 'B-', 'O-'],
            'description': 'Rare Blood Type'
        },
        'AB+': {
            'can_donate_to': ['AB+'],
            'can_receive_from': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
            'description': 'Universal Recipient'
        }
    }
    
    return render_template(
        'main/blood_compatibility.html',
        compatibility_data=compatibility_data,
        title='Blood Compatibility Guide'
    )


@main_bp.route('/privacy-policy')
def privacy_policy():
    """Privacy policy page."""
    return render_template('main/privacy_policy.html', title='Privacy Policy')


@main_bp.route('/terms-of-service')
def terms_of_service():
    """Terms of service page."""
    return render_template('main/terms_of_service.html', title='Terms of Service')


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
    
    # Always redirect to registration form to confirm/update details
    current_user.role = 'patient'
    db.session.commit()
    flash('Please confirm your patient details.', 'info')
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
    
    # Always redirect to registration form to confirm/update details
    current_user.role = 'donor'
    db.session.commit()
    flash('Please confirm your donor details (address, blood group, last donation date).', 'info')
    return redirect(url_for('donor.register'))


@main_bp.route('/delete-all-users-temp-route-12345')
def delete_all_users():
    """Temporary route to delete all users. Remove after use!"""
    try:
        # Delete all related data first
        OTP.query.delete()
        Donor.query.delete()
        Patient.query.delete()
        User.query.delete()
        
        db.session.commit()
        return "All users deleted successfully! Now remove this route from code."
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}"


@main_bp.route('/create-admin-chiranjeevi-temp-route-67890')
def create_admin_chiranjeevi():
    """Temporary route to create admin with Zoho email."""
    try:
        # Check if user exists
        existing_user = User.query.filter_by(email='chiranjeevi.kola@zohomail.in').first()
        
        if existing_user:
            # Update existing user to admin
            existing_user.role = 'admin'
            existing_user.is_verified = True
            existing_user.is_active = True
            existing_user.set_password('g0abdkbxa6')
            db.session.commit()
            return f"User updated to admin! Login at /auth/login with chiranjeevi.kola@zohomail.in"
        else:
            # Create new admin user
            admin = User(
                email='chiranjeevi.kola@zohomail.in',
                phone='+919703065484',
                role='admin',
                is_verified=True,
                is_active=True
            )
            admin.set_password('g0abdkbxa6')
            db.session.add(admin)
            db.session.commit()
            return f"Admin created! Login at /auth/login with chiranjeevi.kola@zohomail.in and password g0abdkbxa6"
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}"
