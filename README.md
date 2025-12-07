# Blood Donation Network

A comprehensive web application built with Python Flask that connects blood donors with patients in need. This platform facilitates easy blood donation management with secure authentication, OTP verification, and role-based access control.

## Features

### 🩸 Core Functionality
- **User Authentication**: Secure registration and login with email/phone OTP verification
- **Role-Based Access**: Three user roles (Admin, Donor, Patient) with specific permissions
- **Donor Management**: Complete donor profiles with blood type, location, and availability status
- **Patient Portal**: Search compatible donors based on blood type and location
- **Admin Dashboard**: Comprehensive user and request management with statistics
- **Feedback System**: Integrated feedback collection on every page

### 🔒 Security Features
- Password hashing with Bcrypt
- CSRF protection on all forms
- SQL injection prevention via SQLAlchemy ORM
- XSS protection
- Rate limiting on OTP requests
- Secure session management
- Environment-based configuration

### 🎨 User Experience
- Responsive design (mobile, tablet, desktop)
- Bootstrap 5 UI framework
- Real-time form validation
- Loading spinners for async operations
- Flash messages for user feedback
- Blood compatibility logic

## Technology Stack

- **Backend**: Python 3.8+, Flask 3.0
- **Database**: PostgreSQL (or MySQL)
- **Authentication**: Flask-Login with OTP
- **Email**: Flask-Mail
- **SMS**: Twilio
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **ORM**: SQLAlchemy
- **Migrations**: Flask-Migrate

## Installation

### Prerequisites
- Python 3.8 or higher
- PostgreSQL (or MySQL)
- pip (Python package manager)
- Virtual environment tool

### Step 1: Clone or Download the Project
```bash
cd blood_donation_network
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup

#### For PostgreSQL:
```bash
# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Create database
createdb blood_donation_db

# Or using psql:
psql postgres
CREATE DATABASE blood_donation_db;
\q
```

#### For MySQL:
```bash
# Install MySQL (macOS)
brew install mysql
brew services start mysql

# Create database
mysql -u root -p
CREATE DATABASE blood_donation_db;
exit;
```

### Step 5: Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Required configurations in .env:**
- `SECRET_KEY`: Generate a strong secret key
- `DATABASE_URL`: Your database connection string
- `MAIL_USERNAME`: Email for sending OTPs
- `MAIL_PASSWORD`: Email app password (for Gmail, use App Password)
- `TWILIO_ACCOUNT_SID`: Twilio account SID (optional, for SMS)
- `TWILIO_AUTH_TOKEN`: Twilio auth token (optional, for SMS)
- `TWILIO_PHONE_NUMBER`: Twilio phone number (optional, for SMS)

**Generating Secret Key:**
```python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Gmail App Password Setup:**
1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account → Security → App Passwords
3. Generate a new app password for "Mail"
4. Use this password in .env file

### Step 6: Initialize Database
```bash
# Initialize Flask-Migrate
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade

# Or use the built-in command:
flask init-db
```

### Step 7: Create Admin User
```bash
# Run the admin creation script
python create_admin.py
```

Follow the prompts to create your first admin account.

### Step 8: Run the Application
```bash
# Development mode
python run.py

# Or using Flask CLI
flask run

# Production mode (using gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

The application will be available at: `http://localhost:5000`

## Usage Guide

### For Donors:
1. Register as a donor with personal and medical information
2. Verify email/phone via OTP
3. Complete profile with blood type, location, and availability
4. Update availability status when ready to donate
5. View donation history in dashboard

### For Patients:
1. Register as a patient
2. Verify account via OTP
3. Create blood request with urgency level
4. Search for compatible donors by blood type and location
5. Contact donors directly via displayed contact information

### For Admins:
1. Login with admin credentials
2. View comprehensive dashboard with statistics
3. Manage users (activate/deactivate accounts)
4. View and manage feedback submissions
5. Export data for reporting

## Blood Compatibility Rules

The application implements proper blood compatibility:
- **O-**: Universal donor (can donate to all)
- **AB+**: Universal recipient (can receive from all)
- **A+**: Can donate to A+, AB+; can receive from A+, A-, O+, O-
- **A-**: Can donate to A+, A-, AB+, AB-; can receive from A-, O-
- **B+**: Can donate to B+, AB+; can receive from B+, B-, O+, O-
- **B-**: Can donate to B+, B-, AB+, AB-; can receive from B-, O-
- **AB-**: Can donate to AB+, AB-; can receive from AB-, A-, B-, O-
- **O+**: Can donate to O+, A+, B+, AB+; can receive from O+, O-

## Project Structure

```
blood_donation_network/
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── models.py                # Database models
│   ├── forms.py                 # WTForms
│   ├── utils.py                 # Helper functions
│   ├── auth/                    # Authentication blueprint
│   ├── donor/                   # Donor blueprint
│   ├── patient/                 # Patient blueprint
│   ├── admin/                   # Admin blueprint
│   ├── main/                    # Main blueprint
│   ├── static/                  # CSS, JS, images
│   └── templates/               # HTML templates
├── migrations/                  # Database migrations
├── instance/                    # Instance-specific files
├── venv/                        # Virtual environment
├── .env                         # Environment variables
├── config.py                    # Configuration
├── run.py                       # Application entry point
├── create_admin.py             # Admin creation script
├── init_db.py                  # Database initialization
└── requirements.txt            # Dependencies
```

## API Endpoints

### Authentication
- `GET/POST /auth/register` - User registration
- `GET/POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `POST /auth/verify-otp` - OTP verification
- `GET/POST /auth/forgot-password` - Password reset request
- `GET/POST /auth/reset-password` - Password reset

### Donor
- `GET /donor/dashboard` - Donor dashboard
- `GET/POST /donor/register` - Donor registration
- `GET /donor/profile` - View profile
- `GET/POST /donor/edit-profile` - Edit profile
- `POST /donor/toggle-availability` - Toggle availability

### Patient
- `GET /patient/dashboard` - Patient dashboard
- `GET/POST /patient/register` - Patient registration
- `GET /patient/search` - Search donors
- `GET /patient/donor/<id>` - View donor details

### Admin
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - Manage users
- `GET /admin/donors` - Manage donors
- `GET /admin/patients` - Manage patients
- `GET /admin/feedback` - Manage feedback
- `POST /admin/user/<id>/toggle` - Activate/deactivate user

### Main
- `GET /` - Homepage
- `GET /about` - About page
- `GET /contact` - Contact page
- `POST /feedback` - Submit feedback

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL/MySQL is running: `pg_isready` or `mysql -u root -p`
- Check DATABASE_URL in .env file
- Ensure database exists: `psql -l` or `SHOW DATABASES;`

### Email OTP Not Sending
- Verify MAIL_USERNAME and MAIL_PASSWORD in .env
- For Gmail, use App Password (not regular password)
- Check spam folder
- Verify MAIL_SERVER and MAIL_PORT settings

### SMS OTP Not Working
- Verify Twilio credentials in .env
- Check Twilio account balance
- Verify phone number format (+1234567890)

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

### Migration Issues
```bash
# Reset migrations
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Security Best Practices

1. **Never commit .env file** - Contains sensitive credentials
2. **Use strong SECRET_KEY** - Generate with `secrets.token_hex(32)`
3. **Enable HTTPS in production** - Set SESSION_COOKIE_SECURE=True
4. **Regular updates** - Keep dependencies updated
5. **Rate limiting** - Already implemented for OTP requests
6. **Input validation** - All forms use WTForms validation
7. **Database backups** - Regular backups recommended

## Production Deployment

### Using Gunicorn
```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# With logging
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - run:app
```

### Environment Variables for Production
```bash
export FLASK_ENV=production
export DEBUG=False
export SESSION_COOKIE_SECURE=True
```

### Nginx Configuration (Optional)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Contributing

This is a complete production-ready application. For modifications:
1. Create a new branch
2. Make changes with proper testing
3. Ensure all tests pass
4. Submit with detailed documentation

## License

This project is provided as-is for educational and production use.

## Support

For issues or questions:
- Check troubleshooting section
- Review Flask documentation: https://flask.palletsprojects.com/
- Check SQLAlchemy docs: https://www.sqlalchemy.org/

## Credits

Built with:
- Flask - Web framework
- Bootstrap - UI framework
- PostgreSQL - Database
- Twilio - SMS service
- Font Awesome - Icons

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Status**: Production Ready
