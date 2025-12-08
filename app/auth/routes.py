"""
Authentication routes for user registration, login, and password management.
"""
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
from app import db
from app.auth import auth_bp
from app.models import User
from app.forms import (
    RegistrationForm, LoginForm,
    ForgotPasswordForm, ResetPasswordForm
)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with email and phone."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Create new user (verified by default, no OTP needed)
            # Don't assign role yet - let user choose
            user = User(
                email=form.email.data.lower(),
                phone=None,  # No phone collected during registration
                role=None,  # No role assigned yet - user will choose
                is_verified=True,  # Auto-verified, no OTP needed
                is_active=True
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please select your role to continue.', 'success')
            
            # Log the user in automatically
            login_user(user, remember=True)
            
            return redirect(url_for('auth.select_role'))
            
        except Exception as e:
            db.session.rollback()
            # Log the actual error for debugging
            print(f"Registration error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # User-friendly error message
            if 'unique constraint' in str(e).lower() or 'duplicate' in str(e).lower():
                if 'email' in str(e).lower():
                    flash('This email is already registered. Please login or use a different email.', 'danger')
                elif 'phone' in str(e).lower():
                    flash('Database error. Please try again or contact support.', 'danger')
                else:
                    flash('This account already exists. Please login.', 'danger')
            else:
                flash('Registration failed. Please try again or contact support.', 'danger')
            
            return render_template('auth/register.html', form=form, title='Register')
    
    return render_template('auth/register.html', form=form, title='Register')


@auth_bp.route('/select-role')
@login_required
def select_role():
    """Allow user to select their role (donor or patient)."""
    # If user already has a role, redirect to appropriate dashboard
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == 'sub_admin':
        return redirect(url_for('admin.sub_admin_dashboard'))
    elif current_user.role == 'donor':
        if current_user.donor:
            return redirect(url_for('donor.dashboard'))
        else:
            return redirect(url_for('donor.register'))
    elif current_user.role == 'patient':
        if current_user.patient:
            return redirect(url_for('patient.dashboard'))
        else:
            return redirect(url_for('patient.register'))
    
    # User has no role yet - show role selection page
    return render_template('auth/select_role.html', title='Select Role')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        # Redirect based on role
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'sub_admin':
            return redirect(url_for('admin.sub_admin_dashboard'))
        elif current_user.role == 'donor':
            return redirect(url_for('donor.dashboard'))
        elif current_user.role == 'patient':
            return redirect(url_for('patient.dashboard'))
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if not user:
            flash('Email address not found. Please check your email or register for a new account.', 'danger')
            return redirect(url_for('auth.login'))
        
        if user and user.check_password(form.password.data):
            # Check if user is blocked
            if user.is_blocked:
                flash('Your account has been blocked by an administrator. Please contact support.', 'danger')
                return redirect(url_for('auth.login'))
            
            # Check if account is deleted
            if user.deleted_at:
                days_since_deletion = (datetime.utcnow() - user.deleted_at).days
                if days_since_deletion <= 30:
                    flash(f'Your account was deleted {days_since_deletion} days ago. Click "Recover Account" to restore it.', 'warning')
                    return render_template('auth/login.html', form=form, title='Login', 
                                         show_recovery=True, recovery_email=user.email)
                else:
                    flash('Your account was permanently deleted after 30 days.', 'danger')
                    return redirect(url_for('auth.login'))
            
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return redirect(url_for('auth.login'))
            
            # Admin and sub-admin login (no OTP required) - CHECK FIRST!
            if user.role == 'admin' or user.role == 'sub_admin':
                login_user(user, remember=form.remember_me.data)
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                if user.role == 'admin':
                    flash('Welcome back, Admin!', 'success')
                    return redirect(url_for('admin.dashboard'))
                else:
                    flash('Welcome back, Sub-Admin!', 'success')
                    return redirect(url_for('admin.sub_admin_dashboard'))
            
            # Check if user has selected a role yet
            if not user.role:
                login_user(user, remember=form.remember_me.data)
                user.last_login = datetime.utcnow()
                db.session.commit()
                flash('Please select your role to continue.', 'info')
                return redirect(url_for('auth.select_role'))
            
            # Check if user has completed profile
            if user.role == 'donor' and not user.donor:
                flash('Please complete your donor profile.', 'info')
                login_user(user, remember=form.remember_me.data)
                user.last_login = datetime.utcnow()
                db.session.commit()
                return redirect(url_for('donor.register'))
            
            if user.role == 'patient' and not user.patient:
                flash('Please complete your patient profile.', 'info')
                login_user(user, remember=form.remember_me.data)
                user.last_login = datetime.utcnow()
                db.session.commit()
                return redirect(url_for('patient.register'))
            
            # Login successful for non-admin users
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'Welcome back, {user.email}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.role == 'donor':
                return redirect(url_for('donor.dashboard'))
            elif user.role == 'patient':
                return redirect(url_for('patient.dashboard'))
            
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html', form=form, title='Login')




@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login with email and password only."""
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    from app.forms import AdminLoginForm
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if not user:
            flash('Invalid credentials.', 'danger')
            return redirect(url_for('auth.admin_login'))
        
        if user.role != 'admin':
            flash('Invalid credentials.', 'danger')
            return redirect(url_for('auth.admin_login'))
        
        if not user.check_password(form.password.data):
            flash('Invalid credentials.', 'danger')
            return redirect(url_for('auth.admin_login'))
        
        if user.is_blocked:
            flash('Your account has been blocked.', 'danger')
            return redirect(url_for('auth.admin_login'))
        
        if user.deleted_at:
            flash('Your account has been deleted.', 'danger')
            return redirect(url_for('auth.admin_login'))
        
        # Direct login without OTP
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        flash('Welcome back, Admin!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('auth/admin_login.html', form=form, title='Admin Login')


@auth_bp.route('/sub-admin-login', methods=['GET', 'POST'])
def sub_admin_login():
    """Sub-admin login - no OTP required."""
    if current_user.is_authenticated and current_user.role == 'sub_admin':
        return redirect(url_for('admin.sub_admin_dashboard'))
    
    from app.forms import LoginForm
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if not user:
            flash('Email address not found. Please check your email.', 'danger')
            return redirect(url_for('auth.sub_admin_login'))
        
        if user and user.role == 'sub_admin':
            if not user.check_password(form.password.data):
                flash('Invalid credentials.', 'danger')
                return redirect(url_for('auth.sub_admin_login'))
            
            if user.is_blocked:
                flash('Your account has been blocked.', 'danger')
                return redirect(url_for('auth.sub_admin_login'))
            
            if user.deleted_at:
                flash('Your account has been deleted.', 'danger')
                return redirect(url_for('auth.sub_admin_login'))
            
            # Login directly without OTP
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Email notifications disabled
            current_app.logger.info(f"Sub-admin login: {user.email}")
            
            flash('Login successful!', 'success')
            return redirect(url_for('admin.sub_admin_dashboard'))
        else:
            flash('Invalid sub-admin credentials.', 'danger')
    
    return render_template('auth/login.html', form=form, title='Sub-Admin Login')





@auth_bp.route('/logout')
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password - disabled for security. Contact admin."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    flash('Password reset is disabled. Please contact administrator for assistance.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Password reset - disabled."""
    return redirect(url_for('auth.forgot_password'))


@auth_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Soft delete user account - can be recovered within 30 days."""
    user = current_user
    
    # Set deletion timestamp
    user.deleted_at = datetime.utcnow()
    user.is_active = False
    
    # Update donor/patient availability
    if user.role == 'donor' and user.donor:
        user.donor.is_available = False
    
    db.session.commit()
    
    # Logout user
    logout_user()
    
    flash('Your account has been deleted. You can recover it within 30 days by logging in.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/recover-account', methods=['POST'])
def recover_account():
    """Recover a deleted account within 30 days."""
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        flash('Please provide email and password.', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        flash('Invalid email or password.', 'danger')
        return redirect(url_for('auth.login'))
    
    if not user.deleted_at:
        flash('This account is not deleted.', 'info')
        return redirect(url_for('auth.login'))
    
    # Check if within 30-day recovery period
    days_since_deletion = (datetime.utcnow() - user.deleted_at).days
    
    if days_since_deletion > 30:
        flash('Recovery period has expired. This account cannot be recovered.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Recover account
    user.deleted_at = None
    user.is_active = True
    db.session.commit()
    
    flash('Your account has been successfully recovered! Please log in.', 'success')
    return redirect(url_for('auth.login'))
