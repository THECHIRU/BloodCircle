# Admin Login with OTP - Instructions

## Important: Use the Correct Login URL

### For Admin Login (with OTP verification):
🔐 **URL:** `http://127.0.0.1:5000/auth/admin-login`

### For Regular User Login (no OTP):
📧 **URL:** `http://127.0.0.1:5000/auth/login`

---

## How Admin Login Works (Updated System)

1. **Visit Admin Login Page**
   - Go to: `http://127.0.0.1:5000/auth/admin-login`
   - Enter your admin email, phone number, and password

2. **OTP Codes Sent**
   - System sends OTP to both your email AND phone
   - Email OTP: Sent to your registered email
   - Phone OTP: Currently shown in console (SMS needs Twilio configuration)

3. **Verify OTP Page**
   - Enter both the Email OTP and Phone OTP
   - Both must be correct to login

4. **Login Successful**
   - After verification, you're logged into admin dashboard
   - Login notification email is sent

---

## Finding Your OTP Codes

### Email OTP:
- Check your email inbox: `chiranjeevi.kola@zohomail.in`
- Subject: "Admin Login OTP - BloodCircle"
- The OTP is a 6-digit code

### Phone OTP:
Since SMS is not configured (requires Twilio), the phone OTP is printed to the **server console**.

**Check the terminal where you ran `python3 run.py`**

You'll see something like:
```
============================================================
📱 PHONE OTP (SMS not configured - showing in console)
============================================================
To: +1234567890
User: Admin
OTP CODE: 123456
============================================================
```

---

## Testing the System

1. **Stop the current server** (Press Ctrl+C in terminal)

2. **Restart the server:**
   ```bash
   cd /Users/chiranjeevikola/Desktop/blood_donation_networkCopilot
   python3 run.py
   ```

3. **Open browser and visit:**
   ```
   http://127.0.0.1:5000/auth/admin-login
   ```

4. **Login with admin credentials:**
   - Email: (your admin email)
   - Phone: (your admin phone)
   - Password: (your admin password)

5. **Watch the terminal for Phone OTP**

6. **Check your email for Email OTP**

7. **Enter both OTPs on the verification page**

---

## Email Configuration

Your email is already configured in `.env`:
- MAIL_USERNAME=chiranjeevi.kola@zohomail.in
- MAIL_SERVER=smtp.gmail.com (Note: This should be smtp.zoho.com for Zoho Mail)

### If email is not working, update `.env`:
```env
MAIL_SERVER=smtp.zoho.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=chiranjeevi.kola@zohomail.in
MAIL_PASSWORD=qemlmodzfgwycwex
MAIL_DEFAULT_SENDER=chiranjeevi.kola@zohomail.in
```

---

## SMS Configuration (Optional)

To enable real SMS OTP, sign up for Twilio and add to `.env`:
```env
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
```

Without Twilio, phone OTPs will be displayed in the console for testing.

---

## Quick Links

- **Admin Login:** http://127.0.0.1:5000/auth/admin-login
- **Regular Login:** http://127.0.0.1:5000/auth/login
- **Home Page:** http://127.0.0.1:5000/
- **Sub-Admin Login:** http://127.0.0.1:5000/auth/sub-admin-login

---

## Troubleshooting

### "No OTP received in email"
1. Check spam/junk folder
2. Verify email settings in `.env`
3. Check server console for error messages

### "Can't find Phone OTP"
- Look at the terminal window where server is running
- OTP is printed in a box with emoji 📱

### "Both OTPs required but only got one"
- Email OTP: Check your email
- Phone OTP: Check server console/terminal

### "OTP expired"
- OTPs expire after 10 minutes
- Request a new OTP by logging in again

---

## Security Features

✅ Dual-factor authentication (Email + Phone)
✅ OTP expires after 10 minutes
✅ Rate limiting (max 5 OTP requests per hour)
✅ Login notification emails
✅ Secure password hashing

---

## Notes

- Regular users (donors/patients) use `/auth/login` - no OTP required
- Sub-admins use `/auth/sub-admin-login` - single OTP (email OR phone)
- Admins use `/auth/admin-login` - dual OTP (email AND phone) ⭐ **NEW**
