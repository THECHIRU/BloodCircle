"""
WTForms for the BloodCircle application.
"""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField, DateField, TextAreaField,
    BooleanField, SubmitField, TelField, EmailField, IntegerField, RadioField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
)
from datetime import datetime, date
from app.models import User


class RegistrationForm(FlaskForm):
    """Base registration form for all users."""
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address'),
        Length(max=120)
    ])
    phone = TelField('Phone Number (Optional)', validators=[
        Optional(),
        Length(min=10, max=20, message='Phone number must be 10-20 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        """Check if email already exists."""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered. Please use a different email.')
    
    def validate_phone(self, field):
        """Check if phone number already exists."""
        if not field.data:  # Skip validation if phone is empty
            return
        # Remove any non-digit characters
        clean_phone = ''.join(filter(str.isdigit, field.data))
        existing_user = User.query.filter(
            User.phone.like(f'%{clean_phone}%')
        ).first()
        if existing_user:
            raise ValidationError('Phone number already registered. Please use a different number.')


class LoginForm(FlaskForm):
    """User login form."""
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class OTPVerificationForm(FlaskForm):
    """OTP verification form."""
    otp = StringField('Enter OTP', validators=[
        DataRequired(message='OTP is required'),
        Length(min=6, max=6, message='OTP must be 6 digits')
    ])
    submit = SubmitField('Verify OTP')
    
    def validate_otp(self, field):
        """Validate OTP format."""
        if not field.data.isdigit():
            raise ValidationError('OTP must contain only digits')


class ForgotPasswordForm(FlaskForm):
    """Forgot password form."""
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    submit = SubmitField('Send Reset OTP')
    
    def validate_email(self, field):
        """Check if email exists."""
        user = User.query.filter_by(email=field.data.lower()).first()
        if not user:
            raise ValidationError('No account found with this email address.')


class ResetPasswordForm(FlaskForm):
    """Reset password form."""
    otp = StringField('OTP Code', validators=[
        DataRequired(message='OTP is required'),
        Length(min=6, max=6, message='OTP must be 6 digits')
    ])
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')


class DonorRegistrationForm(FlaskForm):
    """Donor registration form with complete details."""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=2, max=100, message='Name must be 2-100 characters')
    ])
    blood_group = SelectField('Blood Group', validators=[
        DataRequired(message='Blood group is required')
    ], choices=[
        ('', 'Select Blood Group'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-')
    ])
    date_of_birth = DateField('Date of Birth', validators=[
        DataRequired(message='Date of birth is required')
    ], format='%Y-%m-%d')
    gender = SelectField('Gender', validators=[
        DataRequired(message='Gender is required')
    ], choices=[
        ('', 'Select Gender'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ])
    address = StringField('Street Address', validators=[
        DataRequired(message='Address is required'),
        Length(max=200)
    ])
    city = StringField('City', validators=[
        DataRequired(message='City is required'),
        Length(max=50)
    ])
    state = StringField('State', validators=[
        DataRequired(message='State is required'),
        Length(max=50)
    ])
    pincode = StringField('Pincode', validators=[
        DataRequired(message='Pincode is required'),
        Length(min=5, max=10, message='Invalid pincode')
    ])
    last_donation_date = DateField('Last Donation Date (Optional)', 
                                   validators=[Optional()],
                                   format='%Y-%m-%d')
    medical_history = TextAreaField('Medical History (Optional)',
                                    validators=[Optional(), Length(max=1000)])
    is_available = BooleanField('I am available to donate', default=True)
    submit = SubmitField('Complete Registration')
    
    def validate_date_of_birth(self, field):
        """Validate donor age (must be 18-65)."""
        today = date.today()
        age = today.year - field.data.year - (
            (today.month, today.day) < (field.data.month, field.data.day)
        )
        if age < 18:
            raise ValidationError('You must be at least 18 years old to donate blood.')
        if age > 65:
            raise ValidationError('Donors must be under 65 years old.')
    
    def validate_last_donation_date(self, field):
        """Validate last donation date is not in future."""
        if field.data and field.data > date.today():
            raise ValidationError('Last donation date cannot be in the future.')


class DonorProfileEditForm(FlaskForm):
    """Form for editing donor profile."""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=2, max=100)
    ])
    address = StringField('Street Address', validators=[
        DataRequired(message='Address is required'),
        Length(max=200)
    ])
    city = StringField('City', validators=[
        DataRequired(message='City is required'),
        Length(max=50)
    ])
    state = StringField('State', validators=[
        DataRequired(message='State is required'),
        Length(max=50)
    ])
    pincode = StringField('Pincode', validators=[
        DataRequired(message='Pincode is required'),
        Length(min=5, max=10)
    ])
    last_donation_date = DateField('Last Donation Date (Optional)', 
                                   validators=[Optional()],
                                   format='%Y-%m-%d')
    medical_history = TextAreaField('Medical History (Optional)',
                                    validators=[Optional(), Length(max=1000)])
    is_available = BooleanField('Available to Donate')
    submit = SubmitField('Update Profile')


class PatientRegistrationForm(FlaskForm):
    """Patient registration form."""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=2, max=100)
    ])
    blood_group_required = SelectField('Blood Group Required', validators=[
        DataRequired(message='Blood group is required')
    ], choices=[
        ('', 'Select Blood Group'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-')
    ])
    hospital_name = StringField('Hospital Name', validators=[
        DataRequired(message='Hospital name is required'),
        Length(max=100)
    ])
    location = StringField('Hospital Address', validators=[
        DataRequired(message='Location is required'),
        Length(max=200)
    ])
    city = StringField('City', validators=[
        DataRequired(message='City is required'),
        Length(max=50)
    ])
    state = StringField('State', validators=[
        DataRequired(message='State is required'),
        Length(max=50)
    ])
    urgency_level = SelectField('Urgency Level', validators=[
        DataRequired(message='Urgency level is required')
    ], choices=[
        ('', 'Select Urgency'),
        ('Critical', 'Critical - Immediate Need'),
        ('Urgent', 'Urgent - Within 24 Hours'),
        ('Normal', 'Normal - Within a Week')
    ])
    required_by_date = DateField('Required By Date', validators=[
        DataRequired(message='Required by date is needed')
    ], format='%Y-%m-%d')
    medical_condition = TextAreaField('Medical Condition (Optional)',
                                     validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Complete Registration')
    
    def validate_required_by_date(self, field):
        """Validate required date is not in past."""
        if field.data < date.today():
            raise ValidationError('Required by date cannot be in the past.')


class SearchDonorForm(FlaskForm):
    """Form for searching blood donors."""
    blood_group = SelectField('Blood Group', validators=[Optional()], choices=[
        ('', 'All Blood Groups'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-')
    ])
    city = StringField('City', validators=[Optional()])
    state = StringField('State', validators=[Optional()])
    available_only = BooleanField('Show Available Donors Only', default=True)
    submit = SubmitField('Search')


class FeedbackForm(FlaskForm):
    """Feedback and contact form."""
    name = StringField('Your Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100)
    ])
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address'),
        Length(max=120)
    ])
    subject = StringField('Subject', validators=[
        DataRequired(message='Subject is required'),
        Length(min=5, max=200)
    ])
    message = TextAreaField('Message', validators=[
        DataRequired(message='Message is required'),
        Length(min=10, max=2000, message='Message must be 10-2000 characters')
    ])
    rating = SelectField('Rating (Optional)', validators=[Optional()], choices=[
        ('', 'Select Rating'),
        ('5', '⭐⭐⭐⭐⭐ Excellent'),
        ('4', '⭐⭐⭐⭐ Very Good'),
        ('3', '⭐⭐⭐ Good'),
        ('2', '⭐⭐ Fair'),
        ('1', '⭐ Poor')
    ])
    submit = SubmitField('Submit Feedback')


class AdminLoginForm(FlaskForm):
    """Admin login form."""
    email = EmailField('Admin Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    submit = SubmitField('Admin Login')


class AdminFeedbackResponseForm(FlaskForm):
    """Form for admin to respond to feedback."""
    admin_response = TextAreaField('Response', validators=[
        DataRequired(message='Response is required'),
        Length(min=10, max=2000)
    ])
    submit = SubmitField('Send Response')


class ChangePasswordForm(FlaskForm):
    """Form for changing password."""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')


class ResendOTPForm(FlaskForm):
    """Form for resending OTP."""
    submit = SubmitField('Resend OTP')


class AdminLoginForm(FlaskForm):
    """Admin login form with enhanced security - requires email AND phone."""
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    phone = StringField('Phone Number', validators=[
        DataRequired(message='Phone number is required'),
        Length(min=10, max=20, message='Invalid phone number')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Admin Login')


class SubAdminLoginForm(FlaskForm):
    """Sub-admin login form - can use email or phone OTP."""
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    otp_method = RadioField('Verification Method', 
                           choices=[('email', 'Email OTP'), ('phone', 'Phone OTP')],
                           default='email',
                           validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Request OTP')


class LoginOTPForm(FlaskForm):
    """OTP verification form for login."""
    otp = StringField('Enter OTP', validators=[
        DataRequired(message='OTP is required'),
        Length(min=6, max=6, message='OTP must be 6 digits')
    ])
    submit = SubmitField('Verify & Login')


class AdminLoginOTPForm(FlaskForm):
    """OTP verification form for admin login - requires both email and phone OTP."""
    email_otp = StringField('Email OTP', validators=[
        DataRequired(message='Email OTP is required'),
        Length(min=6, max=6, message='OTP must be 6 digits')
    ])
    phone_otp = StringField('Phone OTP', validators=[
        DataRequired(message='Phone OTP is required'),
        Length(min=6, max=6, message='OTP must be 6 digits')
    ])
    submit = SubmitField('Verify & Login')
    
    def validate_email_otp(self, field):
        """Validate email OTP format."""
        if not field.data.isdigit():
            raise ValidationError('Email OTP must contain only digits')
    
    def validate_phone_otp(self, field):
        """Validate phone OTP format."""
        if not field.data.isdigit():
            raise ValidationError('Phone OTP must contain only digits')
