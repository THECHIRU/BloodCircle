# BloodCircle - Blood Donation Network 🩸

A streamlined web platform connecting blood donors with patients in need, built with Flask and PostgreSQL.

## 🌟 Features

- **Donor Management**: Registration, profile management, availability tracking
- **Patient Features**: Search donors by blood group and location
- **Admin Dashboard**: Complete CRUD operations, user management
- **Data Persistence**: All data preserved across redeployments
- **Simple Authentication**: Password-only login, no OTP required

## 🚀 Quick Deploy to Render

1. Create PostgreSQL database on Render: `blood-donation-db`
2. Create web service from this GitHub repo
3. Link database to web service
4. Deploy - Done in 5 minutes!

## 🔐 Default Admin

```
Email: chiranjeevi.kola@zohomail.in
Password: g0abdkbxa6
```

Login at: `/auth/admin-login` (no OTP needed)

## 💻 Local Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_admin.py
python run.py
```

## 📦 Tech Stack

- Flask 3.0 + PostgreSQL
- Flask-Login authentication
- SQLAlchemy ORM
- Gunicorn server
- Render deployment

## 🔄 Data Persistence

✅ All user data persists across redeployments  
✅ PostgreSQL database independent of web service  
✅ No data loss on updates

## 📚 Documentation

- [QUICK_START.md](QUICK_START.md) - 5-minute deployment guide
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Detailed instructions

---

**Built for saving lives** | [GitHub](https://github.com/THECHIRU/BloodCircle)
