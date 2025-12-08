# 🚀 Render Deployment Quick Start

## Prerequisites Checklist
- [ ] GitHub repository created and code pushed
- [ ] Render account created (free tier)
- [ ] Gmail account ready (for email OTP - optional)
- [ ] Twilio account (for SMS OTP - optional)

## Deployment Steps

### 1. Create PostgreSQL Database on Render
```
Dashboard → New + → PostgreSQL
- Name: blood-donation-db
- Database: blood_donation
- User: blood_donation_user  
- Plan: Free
```

### 2. Create Web Service on Render
```
Dashboard → New + → Web Service
- Connect GitHub repo
- Name: blood-donation-network
- Runtime: Python 3
- Build Command: chmod +x build.sh && ./build.sh
- Start Command: gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 run:app
- Plan: Free
```

### 3. Essential Environment Variables
```
FLASK_ENV=production
SECRET_KEY=(auto-generated, keep it)
DATABASE_URL=(link to blood-donation-db)
PYTHON_VERSION=3.11.0
```

### 4. Optional: Email Configuration
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### 5. Link Database
```
Web Service → Environment → DATABASE_URL → Add Database
Select: blood-donation-db
```

### 6. Deploy
Click "Manual Deploy" or push to GitHub for auto-deploy

## Default Admin Credentials
```
Email: chiranjeevi.kola@zohomail.in
Password: g0abdkbxa6
```
⚠️ **CHANGE PASSWORD IMMEDIATELY AFTER FIRST LOGIN!**

## Testing Checklist
- [ ] Homepage loads: https://your-app.onrender.com
- [ ] Admin login works: /auth/admin_login
- [ ] Admin dashboard accessible
- [ ] User registration works
- [ ] User login works
- [ ] Donor registration works
- [ ] Patient registration works
- [ ] Donor search works
- [ ] Admin CRUD operations work

## Post-Deployment
1. Login as admin
2. Change admin password
3. Test user signup/signin flow
4. Test all modules (donor, patient, admin)
5. Configure email if needed
6. Monitor logs for errors

## Troubleshooting
**Build fails?** → Check logs in Render dashboard
**Database errors?** → Verify DATABASE_URL is linked
**Admin not created?** → Run `python init_admin.py` in Render shell
**Email not working?** → Verify Gmail app password (not regular password)

## Quick Commands (Render Shell)
```bash
# Check database connection
python -c "from app import create_app, db; app=create_app('production'); app.app_context().push(); print(db.engine.url)"

# Recreate admin
python init_admin.py

# Check Python version
python --version
```

## Resources
- Full Guide: See DEPLOYMENT_GUIDE.md
- Render Docs: https://render.com/docs/deploy-flask
- App Repo: https://github.com/THECHIRU/BloodCircle

---

**Deployment Time**: ~10 minutes
**Cost**: $0 (Free tier)
**Auto-deploy**: Enabled on git push
