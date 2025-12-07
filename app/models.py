"""
Database models for the BloodCircle application.
"""
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """
    User model for authentication and authorization.
    Supports three roles: admin, donor, patient
    """
    __tablename__ = 'users'
    __table_args__ = (
        db.Index('ix_users_phone_partial', 'phone', postgresql_where=db.text('phone IS NOT NULL')),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True, index=False, unique=False)  # No unique, no index
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=True)  # admin, donor, patient - nullable until user selects
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    donor = db.relationship('Donor', backref='user', uselist=False, cascade='all, delete-orphan')
    patient = db.relationship('Patient', backref='user', uselist=False, cascade='all, delete-orphan')
    otps = db.relationship('OTP', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Donor(db.Model):
    """
    Donor model storing blood donor information.
    """
    __tablename__ = 'donors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False, index=True)  # A+, A-, B+, B-, O+, O-, AB+, AB-
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # Male, Female, Other
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False, index=True)
    state = db.Column(db.String(50), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    last_donation_date = db.Column(db.Date)
    medical_history = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_age(self):
        """Calculate donor's age."""
        today = datetime.today().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def can_donate(self):
        """Check if donor is eligible to donate based on last donation date."""
        if not self.last_donation_date:
            return True
        
        # Donors can donate every 3 months (90 days)
        days_since_last_donation = (datetime.today().date() - self.last_donation_date).days
        return days_since_last_donation >= 90
    
    def __repr__(self):
        return f'<Donor {self.full_name} - {self.blood_group}>'


class Patient(db.Model):
    """
    Patient model for users seeking blood donations.
    """
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    blood_group_required = db.Column(db.String(5), nullable=False, index=True)
    hospital_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False, index=True)
    state = db.Column(db.String(50), nullable=False)
    urgency_level = db.Column(db.String(20), nullable=False)  # Critical, Urgent, Normal
    required_by_date = db.Column(db.Date, nullable=False)
    medical_condition = db.Column(db.Text)
    is_fulfilled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_urgent(self):
        """Check if request is still urgent based on required date."""
        return self.required_by_date >= datetime.today().date()
    
    def days_remaining(self):
        """Calculate days remaining until required date."""
        return (self.required_by_date - datetime.today().date()).days
    
    def __repr__(self):
        return f'<Patient {self.full_name} - Needs {self.blood_group_required}>'


class Feedback(db.Model):
    """
    Feedback model for user feedback and contact messages.
    """
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)  # 1-5 stars
    is_resolved = db.Column(db.Boolean, default=False)
    admin_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Feedback from {self.name} - {self.subject}>'


class OTP(db.Model):
    """
    OTP model for email and phone verification.
    """
    __tablename__ = 'otps'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    otp_code = db.Column(db.String(255), nullable=False)  # Stored as hash
    otp_type = db.Column(db.String(20), nullable=False)  # email, phone, password_reset
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_valid(self):
        """Check if OTP is still valid (not expired and not used)."""
        return not self.is_used and datetime.utcnow() < self.expires_at
    
    def set_otp(self, otp_code):
        """Hash and set OTP code."""
        self.otp_code = generate_password_hash(otp_code)
    
    def check_otp(self, otp_code):
        """Verify OTP code against stored hash."""
        return check_password_hash(self.otp_code, otp_code)
    
    @staticmethod
    def create_otp(user_id=None, email=None, phone=None, otp_type='email', expiry_minutes=10):
        """
        Create a new OTP record.
        
        Args:
            user_id: User ID (optional)
            email: Email address
            phone: Phone number
            otp_type: Type of OTP (email, phone, password_reset)
            expiry_minutes: OTP validity in minutes
        
        Returns:
            tuple: (OTP object, plain OTP code)
        """
        import random
        
        # Generate 6-digit OTP
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Create OTP record
        otp = OTP(
            user_id=user_id,
            email=email,
            phone=phone,
            otp_type=otp_type,
            expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes)
        )
        otp.set_otp(otp_code)
        
        return otp, otp_code
    
    def __repr__(self):
        return f'<OTP {self.otp_type} - {self.email or self.phone}>'


# Blood compatibility mapping
BLOOD_COMPATIBILITY = {
    'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],  # Universal donor
    'O+': ['O+', 'A+', 'B+', 'AB+'],
    'A-': ['A-', 'A+', 'AB-', 'AB+'],
    'A+': ['A+', 'AB+'],
    'B-': ['B-', 'B+', 'AB-', 'AB+'],
    'B+': ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+']  # Universal recipient
}


def get_compatible_blood_groups(blood_group_required):
    """
    Get list of blood groups that can donate to the required blood group.
    
    Args:
        blood_group_required (str): Blood group needed
    
    Returns:
        list: List of compatible donor blood groups
    """
    compatible_groups = []
    for donor_group, can_donate_to in BLOOD_COMPATIBILITY.items():
        if blood_group_required in can_donate_to:
            compatible_groups.append(donor_group)
    return compatible_groups
