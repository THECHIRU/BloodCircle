"""
Utility functions for OTP generation, email, and SMS services.
"""
import random
from datetime import datetime, timedelta
from flask import current_app, url_for
from flask_mail import Message
from app import mail, db
from app.models import OTP, User


def generate_otp():
    """Generate a 6-digit OTP code."""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def check_otp_rate_limit(user_id=None, email=None, phone=None):
    """
    Check if user has exceeded OTP request rate limit.
    
    Args:
        user_id: User ID
        email: Email address
        phone: Phone number
    
    Returns:
        bool: True if within rate limit, False if exceeded
    """
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    # Count OTPs created in the last hour
    query = OTP.query.filter(OTP.created_at >= one_hour_ago)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    elif email:
        query = query.filter_by(email=email)
    elif phone:
        query = query.filter_by(phone=phone)
    
    count = query.count()
    max_requests = current_app.config.get('MAX_OTP_REQUESTS_PER_HOUR', 3)
    
    return count < max_requests


def send_email_otp(email, otp_code, user_name="User", purpose="verification"):
    """
    Send OTP via email.
    
    Args:
        email: Recipient email address
        otp_code: OTP code to send
        user_name: Recipient name
        purpose: Purpose of OTP (verification, password_reset, login verification)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        subject = "Your BloodCircle OTP"
        
        if purpose == "password_reset":
            subject = "Password Reset OTP - BloodCircle"
            body = f"""
            Dear {user_name},
            
            You have requested to reset your password for BloodCircle.
            
            Your OTP code is: {otp_code}
            
            This code will expire in {current_app.config.get('OTP_EXPIRY_MINUTES', 10)} minutes.
            
            If you did not request this password reset, please ignore this email.
            
            Best regards,
            BloodCircle Team
            """
        elif purpose == "login verification":
            subject = "Admin Login OTP - BloodCircle"
            body = f"""
            Dear {user_name},
            
            Your login OTP code is: {otp_code}
            
            This code will expire in {current_app.config.get('OTP_EXPIRY_MINUTES', 10)} minutes.
            
            If you did not request this login, please secure your account immediately.
            
            Best regards,
            BloodCircle Security Team
            """
        else:
            body = f"""
            Dear {user_name},
            
            Thank you for registering with BloodCircle!
            
            Your OTP code is: {otp_code}
            
            Please enter this code to verify your account. This code will expire in {current_app.config.get('OTP_EXPIRY_MINUTES', 10)} minutes.
            
            Best regards,
            BloodCircle Team
            """
        
        # Check if mail is configured
        if not current_app.config.get('MAIL_USERNAME'):
            current_app.logger.warning(f"Email not configured. OTP for {email}: {otp_code}")
            print(f"\n{'='*60}")
            print(f"📧 EMAIL OTP (Email not configured - showing in console)")
            print(f"{'='*60}")
            print(f"To: {email}")
            print(f"User: {user_name}")
            print(f"Purpose: {purpose}")
            print(f"OTP CODE: {otp_code}")
            print(f"{'='*60}\n")
            return False
        
        msg = Message(
            subject=subject,
            recipients=[email],
            body=body
        )
        
        mail.send(msg)
        current_app.logger.info(f"Email OTP sent successfully to {email}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email OTP to {email}: {str(e)}")
        # Print OTP to console for testing
        print(f"\n{'='*60}")
        print(f"⚠️  EMAIL FAILED - OTP CODE FOR TESTING")
        print(f"{'='*60}")
        print(f"To: {email}")
        print(f"User: {user_name}")
        print(f"Purpose: {purpose}")
        print(f"OTP CODE: {otp_code}")
        print(f"Error: {str(e)}")
        print(f"{'='*60}\n")
        return False


def send_sms_otp(phone, otp_code):
    """
    Send OTP via SMS using Twilio.
    
    Args:
        phone: Phone number in E.164 format (+1234567890)
        otp_code: OTP code to send
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        from twilio.rest import Client
        
        account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        twilio_phone = current_app.config.get('TWILIO_PHONE_NUMBER')
        
        # Skip SMS if Twilio is not configured
        if not all([account_sid, auth_token, twilio_phone]):
            current_app.logger.warning("Twilio not configured, skipping SMS OTP")
            return False
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=f"Your BloodCircle OTP is: {otp_code}. Valid for {current_app.config.get('OTP_EXPIRY_MINUTES', 10)} minutes.",
            from_=twilio_phone,
            to=phone
        )
        
        current_app.logger.info(f"SMS sent successfully: {message.sid}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send SMS OTP to {phone}: {str(e)}")
        return False


def create_and_send_otp(user_id=None, email=None, phone=None, otp_type='email', user_name="User"):
    """
    Create OTP record and send via email/SMS.
    
    Args:
        user_id: User ID
        email: Email address
        phone: Phone number
        otp_type: Type of OTP (email, phone, password_reset)
        user_name: User's name for email
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Check rate limit
    if not check_otp_rate_limit(user_id, email, phone):
        return False, "Too many OTP requests. Please try again later."
    
    # Invalidate previous unused OTPs
    if user_id:
        OTP.query.filter_by(user_id=user_id, is_used=False).update({'is_used': True})
    if email:
        OTP.query.filter_by(email=email, is_used=False).update({'is_used': True})
    if phone:
        OTP.query.filter_by(phone=phone, is_used=False).update({'is_used': True})
    
    db.session.commit()
    
    # Create new OTP
    expiry_minutes = current_app.config.get('OTP_EXPIRY_MINUTES', 10)
    otp_record, otp_code = OTP.create_otp(
        user_id=user_id,
        email=email,
        phone=phone,
        otp_type=otp_type,
        expiry_minutes=expiry_minutes
    )
    
    db.session.add(otp_record)
    db.session.commit()
    
    # Send OTP
    email_sent = False
    sms_sent = False
    
    if email:
        purpose = "password_reset" if otp_type == "password_reset" else "verification"
        email_sent = send_email_otp(email, otp_code, user_name, purpose)
    
    if phone and otp_type != "password_reset":
        sms_sent = send_sms_otp(phone, otp_code)
    
    if email_sent or sms_sent:
        return True, "OTP sent successfully!"
    else:
        return False, "Failed to send OTP. Please try again."


def verify_otp(otp_code, user_id=None, email=None, phone=None, otp_type='email'):
    """
    Verify OTP code.
    
    Args:
        otp_code: OTP code to verify
        user_id: User ID
        email: Email address
        phone: Phone number
        otp_type: Type of OTP
    
    Returns:
        tuple: (success: bool, message: str, otp_record: OTP or None)
    """
    # Find matching OTP
    query = OTP.query.filter_by(otp_type=otp_type, is_used=False)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if email:
        query = query.filter_by(email=email)
    if phone:
        query = query.filter_by(phone=phone)
    
    otp_record = query.order_by(OTP.created_at.desc()).first()
    
    if not otp_record:
        return False, "Invalid OTP code.", None
    
    if not otp_record.is_valid():
        return False, "OTP has expired. Please request a new one.", None
    
    if not otp_record.check_otp(otp_code):
        return False, "Invalid OTP code.", None
    
    # Mark OTP as used
    otp_record.is_used = True
    db.session.commit()
    
    return True, "OTP verified successfully!", otp_record


def send_notification_email(recipient_email, subject, body):
    """
    Send a general notification email.
    
    Args:
        recipient_email: Recipient email address
        subject: Email subject
        body: Email body
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            body=body
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        return False


def send_blood_request_notification(donor_email, donor_name, patient_name, blood_group, location):
    """
    Notify donor about a matching blood request.
    
    Args:
        donor_email: Donor's email
        donor_name: Donor's name
        patient_name: Patient's name
        blood_group: Required blood group
        location: Patient's location
    
    Returns:
        bool: True if sent successfully
    """
    subject = f"Blood Donation Request - {blood_group} Needed"
    body = f"""
    Dear {donor_name},
    
    A patient needs blood donation that matches your blood group!
    
    Details:
    - Patient Name: {patient_name}
    - Blood Group Required: {blood_group}
    - Location: {location}
    
    Please log in to your dashboard to view more details and contact information.
    
    Your generosity can save a life!
    
    Best regards,
    BloodCircle Team
    """
    
    return send_notification_email(donor_email, subject, body)


def send_donor_match_notification(patient_email, patient_name, donor_count, blood_group, city):
    """
    Notify patient about matching donors available.
    
    Args:
        patient_email: Patient's email
        patient_name: Patient's name
        donor_count: Number of matching donors
        blood_group: Required blood group
        city: Patient's city
    
    Returns:
        bool: True if sent successfully
    """
    subject = f"Matching Blood Donors Found - {blood_group}"
    body = f"""
Dear {patient_name},

Good news! We found {donor_count} matching donor(s) for your blood requirement.

Your Requirements:
- Blood Group Needed: {blood_group}
- Location: {city}

Please log in to your dashboard to view donor details and contact information.

Best regards,
BloodCircle Team
    """
    
    return send_notification_email(patient_email, subject, body)


def notify_matching_donors(patient):
    """
    Notify all matching donors when a new patient registers.
    
    Args:
        patient: Patient object
    """
    from app.models import Donor, get_compatible_blood_groups
    
    try:
        # Get compatible blood groups
        compatible_groups = get_compatible_blood_groups(patient.blood_group_required)
        
        # Find available donors with compatible blood groups in same city
        matching_donors = Donor.query.filter(
            Donor.blood_group.in_(compatible_groups),
            Donor.is_available == True,
            Donor.city.ilike(f'%{patient.city}%')
        ).all()
        
        # Send notifications to donors
        donor_count = 0
        for donor in matching_donors:
            if donor.user and donor.user.email and donor.can_donate():
                send_blood_request_notification(
                    donor_email=donor.user.email,
                    donor_name=donor.full_name,
                    patient_name=patient.full_name,
                    blood_group=patient.blood_group_required,
                    location=f"{patient.city}, {patient.state}"
                )
                donor_count += 1
        
        # Send notification to patient if donors found
        if donor_count > 0 and patient.user and patient.user.email:
            send_donor_match_notification(
                patient_email=patient.user.email,
                patient_name=patient.full_name,
                donor_count=donor_count,
                blood_group=patient.blood_group_required,
                city=patient.city
            )
        
        current_app.logger.info(f"Notified {donor_count} donors about patient {patient.full_name}")
        
    except Exception as e:
        current_app.logger.error(f"Error notifying matching donors: {str(e)}")


def notify_matching_patients(donor):
    """
    Notify all matching patients when a new donor registers or becomes available.
    
    Args:
        donor: Donor object
    """
    from app.models import Patient, BLOOD_COMPATIBILITY
    
    try:
        # Get blood groups that can receive from this donor
        can_donate_to = BLOOD_COMPATIBILITY.get(donor.blood_group, [])
        
        # Find active patients who need compatible blood in same city
        matching_patients = Patient.query.filter(
            Patient.blood_group_required.in_(can_donate_to),
            Patient.is_fulfilled == False,
            Patient.city.ilike(f'%{donor.city}%')
        ).all()
        
        # Send notifications to patients
        patient_count = 0
        for patient in matching_patients:
            if patient.user and patient.user.email and patient.is_urgent():
                send_donor_available_notification(
                    patient_email=patient.user.email,
                    patient_name=patient.full_name,
                    donor_name=donor.full_name,
                    blood_group=donor.blood_group,
                    location=f"{donor.city}, {donor.state}"
                )
                patient_count += 1
        
        current_app.logger.info(f"Notified {patient_count} patients about donor {donor.full_name}")
        
    except Exception as e:
        current_app.logger.error(f"Error notifying matching patients: {str(e)}")


def send_donor_available_notification(patient_email, patient_name, donor_name, blood_group, location):
    """
    Notify patient that a matching donor is now available.
    
    Args:
        patient_email: Patient's email
        patient_name: Patient's name
        donor_name: Donor's name
        blood_group: Donor's blood group
        location: Donor's location
    
    Returns:
        bool: True if sent successfully
    """
    subject = f"Matching Donor Available - {blood_group}"
    body = f"""
Dear {patient_name},

Great news! A blood donor matching your requirements has become available!

Donor Details:
- Blood Group: {blood_group}
- Location: {location}

Please log in to your dashboard to view complete donor information and contact details.

Best regards,
BloodCircle Team
    """
    
    return send_notification_email(patient_email, subject, body)


def format_phone_number(phone):
    """
    Format phone number to E.164 format for SMS.
    
    Args:
        phone: Phone number
    
    Returns:
        str: Formatted phone number
    """
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


def send_login_notification(user_email, user_role, user_name, login_time, ip_address, user_agent):
    """
    Send login notification email to admin and user.
    For sub-admin, sends to both main admin and sub-admin.
    """
    from flask import current_app
    from flask_mail import Message
    from app import mail
    
    try:
        # Format the login details
        login_details = f"""
        Login Details:
        - User: {user_name} ({user_email})
        - Role: {user_role.upper()}
        - Time: {login_time}
        - IP Address: {ip_address}
        - Device: {user_agent}
        """
        
        # Create email message
        msg = Message(
            subject=f'🔐 Login Alert - {user_role.upper()} Login Detected',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[]
        )
        
        msg.body = f"""
Dear Admin,

A login was detected on BloodCircle platform.

{login_details}

If this wasn't you or you don't recognize this activity, please take immediate action.

Best regards,
BloodCircle Security Team
        """
        
        msg.html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
        .details {{ background: white; padding: 20px; border-left: 4px solid #dc3545; margin: 20px 0; }}
        .details p {{ margin: 10px 0; }}
        .footer {{ background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
        .alert {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Login Alert</h1>
            <p>Security Notification from BloodCircle</p>
        </div>
        <div class="content">
            <h2>Login Detected</h2>
            <p>A new login was detected on your BloodCircle account.</p>
            
            <div class="details">
                <h3>Login Details:</h3>
                <p><strong>User:</strong> {user_name} ({user_email})</p>
                <p><strong>Role:</strong> <span style="color: #dc3545; font-weight: bold;">{user_role.upper()}</span></p>
                <p><strong>Time:</strong> {login_time}</p>
                <p><strong>IP Address:</strong> {ip_address}</p>
                <p><strong>Device:</strong> {user_agent}</p>
            </div>
            
            <div class="alert">
                <strong>⚠️ Security Notice:</strong> If this wasn't you or you don't recognize this activity, please change your password immediately and contact support.
            </div>
        </div>
        <div class="footer">
            <p><strong>BloodCircle Security Team</strong></p>
            <p>Contact: chiranjeevi.kola@zohomail.in | +91 9703065484</p>
            <p>Repalle, Andhra Pradesh, India</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Determine recipients based on role
        if user_role == 'admin':
            # Send to admin only
            msg.recipients = [user_email]
        elif user_role == 'sub_admin':
            # Send to both admin and sub-admin
            from app.models import User
            admin_user = User.query.filter_by(role='admin').first()
            msg.recipients = [user_email]
            if admin_user:
                msg.recipients.append(admin_user.email)
        else:
            # For donors/patients, send to admin
            from app.models import User
            admin_user = User.query.filter_by(role='admin').first()
            if admin_user:
                msg.recipients = [admin_user.email]
        
        # Send email
        mail.send(msg)
        return True, "Login notification sent successfully"
    
    except Exception as e:
        current_app.logger.error(f"Failed to send login notification: {str(e)}")
        return False, str(e)


def send_otp_for_login(user_id, email=None, phone=None, otp_type='email'):
    """
    Send OTP for admin/sub-admin login verification.
    Can send to either email or phone.
    """
    from flask import current_app
    import random
    from datetime import datetime, timedelta
    from app.models import OTP, User
    from app import db
    
    try:
        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        
        # Get user details
        user = User.query.get(user_id)
        if not user:
            return False, "User not found", None
        
        user_name = "User"
        if user.donor:
            user_name = user.donor.full_name
        elif user.patient:
            user_name = user.patient.full_name
        elif user.role == 'admin':
            user_name = 'Admin'
        elif user.role == 'sub_admin':
            user_name = 'Sub-Admin'
        
        # Delete old OTPs for this type
        OTP.query.filter_by(user_id=user_id, otp_type=f'login_{otp_type}', is_used=False).delete()
        
        # Create new OTP record - store plaintext for now (hash it properly in production)
        otp_record = OTP(
            user_id=user_id,
            email=email,
            phone=phone,
            otp_type=f'login_{otp_type}',
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        # Set the OTP code (will be hashed in the model)
        otp_record.set_otp(otp_code)
        
        db.session.add(otp_record)
        db.session.commit()
        
        # Send OTP based on type
        if otp_type == 'email' and email:
            success = send_email_otp(email, otp_code, user_name, "login verification")
            # Return success even if email fails (OTP is printed to console for testing)
            return True, f"OTP sent to {email} (check console if email not configured)", otp_record
        elif otp_type == 'phone' and phone:
            # Try SMS first
            sms_success = send_sms_otp(phone, otp_code)
            
            if not sms_success:
                # Fallback 1: Send phone OTP to email if email is available
                if email:
                    email_subject = f"Phone OTP for Login - {phone}"
                    email_body = f"""
Dear {user_name},

Your phone OTP for login verification is: {otp_code}

Phone Number: {phone}

This code will expire in {current_app.config.get('OTP_EXPIRY_MINUTES', 10)} minutes.

Note: SMS service is not configured, so we sent this to your email instead.

Best regards,
BloodCircle Security Team
                    """
                    try:
                        from flask_mail import Message
                        from app import mail
                        msg = Message(
                            subject=email_subject,
                            recipients=[email],
                            body=email_body
                        )
                        mail.send(msg)
                        current_app.logger.info(f"Phone OTP sent to email {email} (SMS not configured)")
                        return True, f"Phone OTP sent to your email (SMS not configured)", otp_record
                    except Exception as e:
                        current_app.logger.error(f"Failed to send phone OTP via email: {str(e)}")
                
                # Fallback 2: Print to console for testing
                print(f"\n{'='*60}")
                print(f"📱 PHONE OTP (SMS not configured - showing in console)")
                print(f"{'='*60}")
                print(f"To: {phone}")
                print(f"User: {user_name}")
                print(f"OTP CODE: {otp_code}")
                print(f"{'='*60}\n")
                current_app.logger.info(f"Phone OTP for {phone}: {otp_code}")
                return True, f"Phone OTP: {otp_code} (check console - SMS not configured)", otp_record
            
            return True, f"SMS OTP sent to {phone}", otp_record
        else:
            return False, "Invalid OTP type or missing contact", None
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error sending login OTP: {str(e)}")
        return False, str(e), None


def verify_login_otp(otp_code, user_id, otp_type='email'):
    """
    Verify OTP for sub-admin login.
    """
    from datetime import datetime
    from app.models import OTP
    from app import db
    
    try:
        # Find all unused OTP records for this user and type
        otp_records = OTP.query.filter_by(
            user_id=user_id,
            otp_type=f'login_{otp_type}',
            is_used=False
        ).all()
        
        if not otp_records:
            return False, "Invalid OTP code", None
        
        # Find the matching OTP record by checking hash
        otp_record = None
        for record in otp_records:
            if record.check_otp(otp_code):
                otp_record = record
                break
        
        if not otp_record:
            return False, "Invalid OTP code", None
        
        # Check if expired
        if datetime.utcnow() > otp_record.expires_at:
            return False, "OTP has expired", None
        
        # Mark as used
        otp_record.is_used = True
        otp_record.used_at = datetime.utcnow()
        db.session.commit()
        
        return True, "OTP verified successfully", otp_record
    
    except Exception as e:
        db.session.rollback()
        return False, str(e), None
