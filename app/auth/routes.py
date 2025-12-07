"""
Authentication routes for user registration, login, and password management.
"""
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
from app import db
from app.auth import auth_bp
from app.models import User, OTP
from app.forms import (
    RegistrationForm, LoginForm, OTPVerificationForm,
    ForgotPasswordForm, ResetPasswordForm
)
from app.utils import create_and_send_otp, verify_otp


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with email and phone."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Create new user (verified by default, no OTP needed)
        # Don't assign role yet - let user choose
        user = User(
            email=form.email.data.lower(),
            phone=form.phone.data if form.phone.data else None,  # Optional phone
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
    
    return render_template('auth/register.html', form=form, title='Register')


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_route():
    """Verify OTP after registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Check if user has a pending verification
    user_id = session.get('pending_user_id')
    email = session.get('pending_email')
    
    if not user_id or not email:
        flash('No pending verification found. Please register first.', 'warning')
        return redirect(url_for('auth.register'))
    
    form = OTPVerificationForm()
    
    if form.validate_on_submit():
        # Verify OTP
        success, message, otp_record = verify_otp(
            otp_code=form.otp.data,
            user_id=user_id,
            email=email,
            otp_type='email'
        )
        
        if success:
            # Mark user as verified
            user = User.query.get(user_id)
            if user:
                user.is_verified = True
                db.session.commit()
                
                # Clear session
                session.pop('pending_user_id', None)
                session.pop('pending_email', None)
                session.pop('pending_phone', None)
                
                flash('Account verified successfully! Please complete your profile.', 'success')
                
                # Redirect to role selection or profile creation
                return redirect(url_for('auth.select_role'))
        else:
            flash(message, 'danger')
    
    return render_template('auth/verify_otp.html', form=form, email=email, title='Verify OTP')


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


@auth_bp.route('/resend-otp', methods=['POST', 'GET'])
def resend_otp():
    """Resend OTP to user."""
    user_id = session.get('pending_user_id')
    email = session.get('pending_email')
    phone = session.get('pending_phone')
    
    if not user_id or not email:
        flash('No pending verification found. Please register first.', 'warning')
        return redirect(url_for('auth.register'))
    
    try:
        success, message = create_and_send_otp(
            user_id=user_id,
            email=email,
            phone=phone,
            otp_type='email',
            user_name='User'
        )
        
        if success:
            flash('OTP has been resent to your email. Please check your inbox (and spam folder).', 'success')
        else:
            flash(f'Failed to resend OTP: {message}. Please try again or contact support.', 'danger')
    except Exception as e:
        flash(f'Error resending OTP: {str(e)}. Please try again.', 'danger')
    
    return redirect(url_for('auth.verify_otp_route'))


@auth_bp.route('/resend-reset-otp', methods=['POST', 'GET'])
def resend_reset_otp():
    """Resend OTP for password reset."""
    email = session.get('reset_email')
    
    if not email:
        flash('Please request a password reset first.', 'warning')
        return redirect(url_for('auth.forgot_password'))
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('Invalid session. Please try again.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    # Send OTP
    success, message = create_and_send_otp(
        user_id=user.id,
        email=user.email,
        otp_type='password_reset',
        user_name=user.donor.full_name if user.donor else (
            user.patient.full_name if user.patient else 'User'
        )
    )
    
    if success:
        flash('OTP resent successfully! Check console for OTP code.', 'success')
    else:
        flash(f'Failed to resend OTP: {message}', 'danger')
    
    return redirect(url_for('auth.reset_password'))


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
    """Enhanced admin login - requires email AND phone verification with OTP."""
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    from app.forms import AdminLoginForm
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if not user:
            flash('Email address not found. Please check your email.', 'danger')
            return redirect(url_for('auth.admin_login'))
        
        if user and user.role == 'admin':
            if user.phone != form.phone.data:
                flash('Invalid credentials. Both email and phone must match.', 'danger')
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
            
            # Send OTP to email only
            from app.utils import send_otp_for_login
            
            # Send email OTP
            email_success, email_msg, _ = send_otp_for_login(user_id=user.id, email=user.email, otp_type='email')
            
            if email_success:
                # Store login details in session
                session['login_user_id'] = user.id
                session['login_otp_type'] = 'email'
                session['remember_me'] = form.remember_me.data
                session['admin_login'] = True
                
                flash(f'OTP sent to {user.email}', 'success')
                return redirect(url_for('auth.verify_admin_login_otp'))
            else:
                flash(f'Failed to send OTP: {email_msg}', 'danger')
        else:
            flash('Invalid admin credentials.', 'danger')
    
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
            
            from app.utils import send_login_notification
            user_name = user.donor.full_name if user.donor else (user.patient.full_name if user.patient else 'Sub-Admin')
            send_login_notification(
                user_email=user.email,
                user_role=user.role,
                user_name=user_name,
                login_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string[:100]
            )
            
            flash('Login successful!', 'success')
            return redirect(url_for('admin.sub_admin_dashboard'))
        else:
            flash('Invalid sub-admin credentials.', 'danger')
    
    return render_template('auth/login.html', form=form, title='Sub-Admin Login')


@auth_bp.route('/verify-login-otp', methods=['GET', 'POST'])
def verify_login_otp():
    """Verify OTP for sub-admin login."""
    user_id = session.get('login_user_id')
    otp_type = session.get('login_otp_type', 'email')
    
    if not user_id:
        flash('No pending login verification. Please login again.', 'warning')
        return redirect(url_for('auth.sub_admin_login'))
    
    from app.forms import LoginOTPForm
    form = LoginOTPForm()
    
    if form.validate_on_submit():
        from app.utils import verify_login_otp as verify_otp_func
        success, message, _ = verify_otp_func(otp_code=form.otp.data, user_id=user_id, otp_type=otp_type)
        
        if success:
            user = User.query.get(user_id)
            if user:
                remember = session.get('remember_me', False)
                login_user(user, remember=remember)
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                from app.utils import send_login_notification
                user_name = user.donor.full_name if user.donor else (user.patient.full_name if user.patient else 'Sub-Admin')
                send_login_notification(
                    user_email=user.email,
                    user_role=user.role,
                    user_name=user_name,
                    login_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string[:100]
                )
                
                session.pop('login_user_id', None)
                session.pop('login_otp_type', None)
                session.pop('remember_me', None)
                
                flash('Login successful!', 'success')
                return redirect(url_for('admin.sub_admin_dashboard'))
        else:
            flash(f'OTP verification failed: {message}', 'danger')
    
    user = User.query.get(user_id)
    contact_info = user.email if otp_type == 'email' else user.phone
    
    return render_template('auth/verify_login_otp.html', form=form, 
                         contact_info=contact_info, otp_type=otp_type, title='Verify Login OTP')


@auth_bp.route('/resend-admin-login-otp', methods=['POST', 'GET'])
def resend_admin_login_otp():
    """Resend OTP for admin login."""
    user_id = session.get('login_user_id')
    is_admin = session.get('admin_login', False)
    
    if not user_id or not is_admin:
        flash('No pending login verification. Please login again.', 'warning')
        return redirect(url_for('auth.admin_login'))
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.admin_login'))
    
    from app.utils import send_otp_for_login
    success, message = send_otp_for_login(user=user, otp_type='email', purpose='login verification')
    
    if success:
        flash('New OTP sent successfully to your email!', 'success')
    else:
        flash(f'Failed to resend OTP: {message}', 'danger')
    
    return redirect(url_for('auth.verify_admin_login_otp'))


@auth_bp.route('/verify-admin-login-otp', methods=['GET', 'POST'])
def verify_admin_login_otp():
    """Verify OTP for admin login - email OTP only."""
    user_id = session.get('login_user_id')
    is_admin = session.get('admin_login', False)
    
    if not user_id or not is_admin:
        flash('No pending login verification. Please login again.', 'warning')
        return redirect(url_for('auth.admin_login'))
    
    from app.forms import LoginOTPForm
    form = LoginOTPForm()
    
    if form.validate_on_submit():
        from app.utils import verify_login_otp as verify_otp_func
        
        # Verify email OTP
        email_success, email_msg, _ = verify_otp_func(otp_code=form.otp.data, user_id=user_id, otp_type='email')
        
        if email_success:
            user = User.query.get(user_id)
            if user:
                remember = session.get('remember_me', False)
                login_user(user, remember=remember)
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                from app.utils import send_login_notification
                user_name = user.donor.full_name if user.donor else (user.patient.full_name if user.patient else 'Admin')
                send_login_notification(
                    user_email=user.email,
                    user_role=user.role,
                    user_name=user_name,
                    login_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string[:100]
                )
                
                session.pop('login_user_id', None)
                session.pop('login_otp_type', None)
                session.pop('remember_me', None)
                session.pop('admin_login', None)
                
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin.dashboard'))
        else:
            flash(f'OTP verification failed: {email_msg}', 'danger')
    
    user = User.query.get(user_id)
    
    return render_template('auth/verify_login_otp.html', form=form, 
                         contact_info=user.email, otp_type='email', 
                         title='Verify Admin Login OTP', is_admin_login=True)


@auth_bp.route('/logout')
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password - request OTP."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user:
            # Check if user is verified
            if not user.is_verified:
                flash('This account is not verified yet. Please verify your account first or contact support.', 'warning')
                return redirect(url_for('auth.forgot_password'))
            
            # Check if user is blocked
            if user.is_blocked:
                flash('This account has been blocked. Please contact support.', 'danger')
                return redirect(url_for('auth.forgot_password'))
            
            # Check if user is deleted
            if user.deleted_at:
                flash('This account has been deleted. Please contact support if you need assistance.', 'danger')
                return redirect(url_for('auth.forgot_password'))
            
            # Check if user is active
            if not user.is_active:
                flash('This account is not active. Please contact support.', 'danger')
                return redirect(url_for('auth.forgot_password'))
            
            # Store email in session
            session['reset_email'] = user.email
            
            # Send OTP
            success, message = create_and_send_otp(
                user_id=user.id,
                email=user.email,
                otp_type='password_reset',
                user_name=user.donor.full_name if user.donor else (
                    user.patient.full_name if user.patient else 'User'
                )
            )
            
            if success:
                flash('Password reset OTP sent to your email.', 'success')
                return redirect(url_for('auth.reset_password'))
            else:
                flash(f'Failed to send OTP: {message}', 'danger')
        else:
            # Don't reveal if email exists or not (security)
            flash('If an account exists with this email, you will receive a password reset OTP.', 'info')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form, title='Forgot Password')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset password with OTP."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    email = session.get('reset_email')
    
    if not email:
        flash('Please request a password reset first.', 'warning')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        # Verify OTP
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Invalid session. Please try again.', 'danger')
            return redirect(url_for('auth.forgot_password'))
        
        success, message, otp_record = verify_otp(
            otp_code=form.otp.data,
            user_id=user.id,
            email=email,
            otp_type='password_reset'
        )
        
        if success:
            # Reset password
            user.set_password(form.password.data)
            db.session.commit()
            
            # Clear session
            session.pop('reset_email', None)
            
            flash('Password reset successfully! Please login with your new password.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
    
    return render_template('auth/reset_password.html', form=form, email=email, title='Reset Password')


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
