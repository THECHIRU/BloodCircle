# Gmail Setup Instructions

## Admin Email: chirukola123@gmail.com

Your admin account has been updated to use **chirukola123@gmail.com**.

## Next Steps:

### 1. Generate Gmail App Password

1. Go to: https://myaccount.google.com/apppasswords
2. You must have 2-Factor Authentication enabled first
3. Select "Mail" or "Other (Custom name)"
4. Name it: "Blood Donation App"
5. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### 2. Update .env File

Open `.env` and replace:
```
MAIL_PASSWORD=REPLACE_WITH_GMAIL_APP_PASSWORD
```

With your generated app password:
```
MAIL_PASSWORD=your_16_char_password_here
```

### 3. Restart Server

Stop the current server (Ctrl+C) and run:
```bash
python3 run.py
```

## Admin Login

- **Email:** chirukola123@gmail.com
- **Login URL:** http://127.0.0.1:5000/auth/admin-login
- **OTP:** Will be sent to your Gmail after configuring the app password

## Changes Made:

✅ Updated admin email from chiranjeevi.kola@zohomail.in to chirukola123@gmail.com
✅ Removed old admin account
✅ Changed role from sub_admin to admin
✅ Configured Gmail SMTP in .env (requires app password)
✅ Account is verified and active

## Important Notes:

- Sub-admin functionality remains in the code but no sub-admin users exist
- Admin login requires email OTP for security
- Make sure to use the Gmail app password, not your regular Gmail password
