#!/usr/bin/env python3
"""
Update auth routes to add:
1. Admin login with email+phone verification
2. Sub-admin login with OTP
3. Login notifications for all users
"""

# Read the current routes file
with open('app/auth/routes.py', 'r') as f:
    lines = f.readlines()

# Find the logout route line
logout_line = None
for i, line in enumerate(lines):
    if line.strip().startswith("@auth_bp.route('/logout')"):
        logout_line = i
        break

if logout_line is None:
    print("Error: Could not find logout route")
    exit(1)

# New routes to insert
new_routes = '''

@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Enhanced admin login - requires email AND phone verification."""
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    from app.forms import AdminLoginForm
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        # Find user by email
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.role == 'admin':
            # Verify BOTH email AND phone match
            if user.phone != form.phone.data:
                flash('Invalid credentials. Both email and phone must match.', 'danger')
                return redirect(url_for('auth.admin_login'))
            
            # Verify password
            if not user.check_password(form.password.data):
                flash('Invalid credentials.', 'danger')
                return redirect(url_for('auth.admin_login'))
            
            # Check account status
            if user.is_blocked:
                flash('Your account has been blocked.', 'danger')
                return redirect(url_for('auth.admin_login'))
            
            if user.deleted_at:
                flash('Your account has been deleted.', 'danger')
                return redirect(url_for('auth.admin_login'))
            
            # Login successful
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Send login notification
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
            
            flash(f'Welcome back, Admin!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
    
    return render_template('auth/admin_login.html', form=form, title='Admin Login')


@auth_bp.route('/sub-admin-login', methods=['GET', 'POST'])
def sub_admin_login():
    """Sub-admin login with OTP verification (email or phone)."""
    if current_user.is_authenticated and current_user.role == 'sub_admin':
        return redirect(url_for('admin.sub_admin_dashboard'))
    
    from app.forms import SubAdminLoginForm
    form = SubAdminLoginForm()
    
    if form.validate_on_submit():
        # Find user by email
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.role == 'sub_admin':
            # Verify password
            if not user.check_password(form.password.data):
                flash('Invalid credentials.', 'danger')
                return redirect(url_for('auth.sub_admin_login'))
            
            # Check account status
            if user.is_blocked:
                flash('Your account has been blocked.', 'danger')
                return redirect(url_for('auth.sub_admin_login'))
            
            if user.deleted_at:
                flash('Your account has been deleted.', 'danger')
                return redirect(url_for('auth.sub_admin_login'))
            
            # Send OTP based on selected method
            from app.utils import send_otp_for_login
            otp_method = form.otp_method.data
            
            if otp_method == 'email':
                success, message, _ = send_otp_for_login(
                    user_id=user.id,
                    email=user.email,
                    otp_type='email'
                )
            else:  # phone
                success, message, _ = send_otp_for_login(
                    user_id=user.id,
                    phone=user.phone,
                    otp_type='phone'
                )
            
            if success:
                # Store in session for OTP verification
                session['login_user_id'] = user.id
                session['login_otp_type'] = otp_method
                session['remember_me'] = form.remember_me.data
                flash(f'OTP sent successfully! {message}', 'success')
                return redirect(url_for('auth.verify_login_otp'))
            else:
                flash(f'Failed to send OTP: {message}', 'danger')
        else:
            flash('Invalid sub-admin credentials.', 'danger')
    
    return render_template('auth/sub_admin_login.html', form=form, title='Sub-Admin Login')


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
        # Verify OTP
        from app.utils import verify_login_otp
        success, message, _ = verify_login_otp(
            otp_code=form.otp.data,
            user_id=user_id,
            otp_type=otp_type
        )
        
        if success:
            # Get user
            user = User.query.get(user_id)
            if user:
                # Login successful
                remember = session.get('remember_me', False)
                login_user(user, remember=remember)
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Send login notification
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
                
                # Clear session
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


'''

# Insert the new routes before the logout route
lines.insert(logout_line, new_routes)

# Also update the regular login to send notifications
# Find the login function and add notification after successful login
updated_lines = []
in_login_function = False
notification_added = False

for i, line in enumerate(lines):
    updated_lines.append(line)
    
    # Check if we're in the login function
    if "@auth_bp.route('/login'" in line:
        in_login_function = True
    
    # Look for the successful login commit
    if in_login_function and not notification_added and 'db.session.commit()' in line and 'user.last_login' in lines[i-1]:
        # Add notification code after this commit
        notification_code = '''            
            # Send login notification
            from app.utils import send_login_notification
            user_name = user.donor.full_name if user.donor else (user.patient.full_name if user.patient else user.email.split('@')[0])
            send_login_notification(
                user_email=user.email,
                user_role=user.role,
                user_name=user_name,
                login_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string[:100]
            )
'''
        updated_lines.append(notification_code)
        notification_added = True

# Write the updated file
with open('app/auth/routes.py', 'w') as f:
    f.writelines(updated_lines)

print("✅ Auth routes updated successfully!")
print("Added:")
print("  - /admin-login route with email+phone verification")
print("  - /sub-admin-login route with OTP")
print("  - /verify-login-otp route")
print("  - Login notifications for all user types")
