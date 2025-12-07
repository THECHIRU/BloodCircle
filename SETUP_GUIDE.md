# Blood Donation Network - Complete Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Production Deployment](#production-deployment)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher**
  ```bash
  python3 --version
  ```

- **PostgreSQL** (recommended) or **MySQL**
  ```bash
  # macOS
  brew install postgresql
  brew services start postgresql
  
  # Ubuntu/Debian
  sudo apt-get install postgresql postgresql-contrib
  sudo service postgresql start
  ```

- **pip** (Python package manager)
  ```bash
  python3 -m pip --version
  ```

- **virtualenv** (recommended)
  ```bash
  pip3 install virtualenv
  ```

## Installation Steps

### Step 1: Navigate to Project Directory

```bash
cd /Users/chiranjeevikola/Desktop/blood_donation_network
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

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages:
- Flask and extensions
- Database drivers (PostgreSQL/MySQL)
- Authentication packages
- Email and SMS services
- And more...

## Configuration

### Step 1: Create Environment File

```bash
# Copy the example environment file
cp .env.example .env
```

### Step 2: Edit .env File

Open `.env` in your text editor and configure the following:

```bash
# Generate a strong secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
```

#### Database Configuration

**For PostgreSQL:**
```env
DATABASE_URL=postgresql://username:password@localhost/blood_donation_db
```

**For MySQL:**
```env
DATABASE_URL=mysql+pymysql://username:password@localhost/blood_donation_db
```

Replace:
- `username` with your database username
- `password` with your database password
- `blood_donation_db` with your database name

#### Email Configuration (Gmail Example)

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

**Important:** For Gmail, you need to create an App Password:
1. Go to Google Account → Security
2. Enable 2-Factor Authentication
3. Go to App Passwords
4. Generate a new app password for "Mail"
5. Use this password in your .env file

#### Twilio Configuration (Optional - for SMS OTP)

```env
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
```

If you don't configure Twilio, the app will still work but SMS OTP will be skipped.

## Database Setup

### Step 1: Create Database

#### PostgreSQL:
```bash
# Using createdb command
createdb blood_donation_db

# Or using psql
psql postgres
CREATE DATABASE blood_donation_db;
\q
```

#### MySQL:
```bash
mysql -u root -p
CREATE DATABASE blood_donation_db;
exit;
```

### Step 2: Initialize Database Tables

```bash
python init_db.py
```

This will:
- Drop existing tables (if any)
- Create all required tables
- Set up the database schema

### Step 3: Create Admin User

```bash
python create_admin.py
```

Follow the prompts to create your admin account:
- Enter admin email
- Enter phone number (with country code)
- Create password (minimum 8 characters)
- Confirm password

**Optional:** Create sample data for testing when prompted.

## Running the Application

### Development Mode

#### Method 1: Using run.py
```bash
python run.py
```

#### Method 2: Using Flask CLI
```bash
flask run
```

#### Method 3: With auto-reload
```bash
export FLASK_ENV=development
export FLASK_APP=run.py
flask run --reload
```

The application will be available at: **http://localhost:5000**

### Production Mode

#### Using Gunicorn (Recommended)

```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with 4 worker processes
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# With logging
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - run:app
```

## Testing

### Test Accounts

If you created sample data during admin setup:

**Donors:**
- Email: donor1@example.com | Password: donor123
- Email: donor2@example.com | Password: donor123

**Patient:**
- Email: patient1@example.com | Password: patient123

**Admin:**
- Use the credentials you created during setup

### Manual Testing Flow

1. **Homepage** - http://localhost:5000
   - Verify statistics display
   - Check navigation links

2. **Registration** - http://localhost:5000/auth/register
   - Register a new user
   - Check OTP email
   - Verify OTP

3. **Role Selection**
   - Choose Donor or Patient
   - Complete profile

4. **Donor Flow**
   - View dashboard
   - Update availability
   - Edit profile

5. **Patient Flow**
   - View dashboard
   - Search for donors
   - View donor details

6. **Admin Flow**
   - Login as admin
   - View statistics
   - Manage users

## Troubleshooting

### Issue: Database Connection Error

**Problem:** Can't connect to database

**Solutions:**
```bash
# Check if PostgreSQL is running
pg_isready

# Or for MySQL
mysql -u root -p -e "SELECT 1"

# Verify DATABASE_URL in .env file
cat .env | grep DATABASE_URL

# Test database connection
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.session.execute('SELECT 1')"
```

### Issue: Email OTP Not Sending

**Problem:** OTP emails not being sent

**Solutions:**
1. Check email credentials in .env
2. For Gmail, ensure you're using App Password, not regular password
3. Check spam folder
4. Verify MAIL_SERVER and MAIL_PORT settings
5. Test email configuration:
   ```python
   from flask_mail import Mail, Message
   from app import create_app
   
   app = create_app()
   mail = Mail(app)
   
   with app.app_context():
       msg = Message('Test', recipients=['test@example.com'], body='Test')
       mail.send(msg)
   ```

### Issue: Import Errors

**Problem:** ModuleNotFoundError

**Solutions:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

### Issue: Migration Errors

**Problem:** Database migration issues

**Solutions:**
```bash
# Reset database (WARNING: This deletes all data)
python init_db.py

# Or manually using Flask-Migrate
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Issue: Port Already in Use

**Problem:** Port 5000 is already in use

**Solutions:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process (replace PID with actual process ID)
kill -9 PID

# Or use a different port
flask run --port 5001
```

### Issue: CSRF Token Missing

**Problem:** CSRF validation error

**Solutions:**
1. Ensure SECRET_KEY is set in .env
2. Check that `{{ form.hidden_tag() }}` is in all forms
3. Clear browser cache and cookies
4. Verify WTF_CSRF_ENABLED is True in config

## Production Deployment

### Environment Setup

1. Set production environment variables:
```bash
export FLASK_ENV=production
export DEBUG=False
```

2. Use production database (not SQLite)

3. Set strong SECRET_KEY

4. Enable HTTPS (SESSION_COOKIE_SECURE=True)

### Using Nginx (Reverse Proxy)

Create `/etc/nginx/sites-available/blood_donation`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/blood_donation_network/app/static;
        expires 30d;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/blood_donation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Using Systemd (Auto-start on boot)

Create `/etc/systemd/system/blood_donation.service`:

```ini
[Unit]
Description=Blood Donation Network
After=network.target

[Service]
User=your-username
WorkingDirectory=/path/to/blood_donation_network
Environment="PATH=/path/to/blood_donation_network/venv/bin"
ExecStart=/path/to/blood_donation_network/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 run:app

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable blood_donation
sudo systemctl start blood_donation
sudo systemctl status blood_donation
```

### SSL/HTTPS with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is set up automatically
sudo certbot renew --dry-run
```

### Database Backups

#### PostgreSQL Backup:
```bash
# Backup
pg_dump blood_donation_db > backup.sql

# Restore
psql blood_donation_db < backup.sql

# Automated daily backups (add to crontab)
0 2 * * * pg_dump blood_donation_db > /backups/blood_$(date +\%Y\%m\%d).sql
```

#### MySQL Backup:
```bash
# Backup
mysqldump -u username -p blood_donation_db > backup.sql

# Restore
mysql -u username -p blood_donation_db < backup.sql
```

### Monitoring

1. **Application Logs**
   ```bash
   tail -f /var/log/blood_donation/error.log
   ```

2. **Nginx Logs**
   ```bash
   tail -f /var/log/nginx/access.log
   tail -f /var/log/nginx/error.log
   ```

3. **System Resource Usage**
   ```bash
   htop
   ```

## Security Checklist

- [ ] Strong SECRET_KEY generated
- [ ] Database credentials secured
- [ ] HTTPS enabled (SESSION_COOKIE_SECURE=True)
- [ ] Debug mode disabled in production
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] Regular security updates
- [ ] Database backups automated
- [ ] Email credentials secured
- [ ] Firewall configured
- [ ] Regular log monitoring

## Additional Resources

- **Flask Documentation:** https://flask.palletsprojects.com/
- **SQLAlchemy Documentation:** https://www.sqlalchemy.org/
- **Bootstrap Documentation:** https://getbootstrap.com/
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs
3. Check Flask/SQLAlchemy documentation
4. Verify all configuration settings

## License

This project is provided as-is for educational and production use.

---

**Version:** 1.0.0  
**Last Updated:** November 2025
