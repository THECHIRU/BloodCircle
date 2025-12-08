# Blood Donation Network - Render Deployment Guide

## 🚀 Quick Deployment (5 Minutes)

### Prerequisites
- GitHub account with repository
- Render account (free tier)

### Step 1: Create PostgreSQL Database
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **PostgreSQL**
3. Configure:
   - Name: `blood-donation-db`
   - Database: `blood_donation`
   - Region: Choose closest to your users
   - Plan: **Free**
4. Click **Create Database**

### Step 2: Deploy Web Service
1. Click **New +** → **Web Service**
2. Connect GitHub repository
3. Configure:
   - Name: `blood-donation-network`
   - Build: `chmod +x build.sh && ./build.sh`
   - Start: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 run:app`
   - Plan: **Free**

### Step 3: Link Database
1. Environment tab → DATABASE_URL → Link to `blood-donation-db`
2. Ensure FLASK_ENV=production
3. SECRET_KEY is auto-generated

### Step 4: Deploy
- Click "Deploy"
- Wait 5-10 minutes
- Done!

## 🔐 Login

```
URL: https://your-app.onrender.com/auth/admin-login
Email: chiranjeevi.kola@zohomail.in
Password: g0abdkbxa6
```

**No OTP required - direct login!**

## ✅ Features

- ✅ Password-only authentication
- ✅ No email configuration needed
- ✅ No SMS/Twilio setup required
- ✅ Data persists across redeployments
- ✅ All CRUD operations work
- ✅ User signup/signin functional

## 🔄 Data Persistence

**All data is automatically preserved:**
- User accounts
- Donor profiles
- Patient records
- Admin settings

PostgreSQL database persists independently of web service deployments.

## 🐛 Troubleshooting

**Build fails?** Check Render logs for specific error

**Can't login?** Verify:
- Email: `chiranjeevi.kola@zohomail.in` (exact)
- Password: `g0abdkbxa6` (case-sensitive)
- No OTP required

**Database errors?** Ensure DATABASE_URL is linked

## 🔄 Updating

```bash
git add .
git commit -m "Update"
git push origin main
# Auto-deploys, data preserved
```

## 📊 Success Criteria

✅ Homepage loads  
✅ Admin can login  
✅ CRUD operations work  
✅ Users can register/login  
✅ Donors can create profiles  
✅ Patients can search donors  
✅ Data persists after redeploy

---

**Deployment time**: ~10 minutes  
**Cost**: $0 (Free tier)  
**Data**: Fully persistent
