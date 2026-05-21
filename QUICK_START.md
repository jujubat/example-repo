# Quick Start Guide - Tap Trip Auth System

## ⚡ 5-Minute Setup

### 1. Install Dependencies
```bash
cd batuma_gprs_weather
pip install flask flask-cors PyJWT waitress
```

### 2. Start Server
```bash
python app_simple.py
```

**Server running on:** http://localhost:8000

### 3. Access Points

| URL | Purpose |
|-----|---------|
| http://localhost:8000/login.html | Login/Sign up |
| http://localhost:8000/dashboard | Admin panel |
| http://localhost:8000/ | Main app |

---

## 🧪 Test It Now

### Create Super Admin Account
1. Go to http://localhost:8000/login.html
2. Click "Sign Up"
3. Fill form:
   ```
   Name: My Admin
   Email: batwiineltdgroup@gmail.com
   Phone: +1234567890
   Password: SecurePass123
   ```
4. Click "Create Account"
5. ✅ Account auto-activated!
6. Click "Login"
7. Enter credentials
8. ✅ Login successful → see "🔐 Admin Panel" link

### Create Regular User
1. On login page, click "Sign Up"
2. Fill form:
   ```
   Name: Test User
   Email: testuser@example.com
   Phone: +9876543210
   Password: SecurePass456
   ```
3. Click "Create Account"
4. ❌ Try to login → Shows "Account is pending"

### Approve as Admin
1. Login as Super Admin (batwiineltdgroup@gmail.com)
2. Click "🔐 Admin Panel"
3. See "Test User" in pending
4. Click "✓ Approve"
5. ✅ Account approved
6. Testuser can now login

---

## 📋 Features

### For Users
- ✅ Signup with email/phone validation
- ✅ Secure password (min 8 chars)
- ✅ Auto-login redirect
- ✅ Profile management
- ✅ Logout

### For Admins
- ✅ View all pending accounts
- ✅ Approve/Reject accounts
- ✅ See all users list
- ✅ Change user roles
- ✅ View role capabilities
- ✅ Auto-activation when details complete

### Special Feature
- ✅ **Super Admin Auto-Activation:** Email `batwiineltdgroup@gmail.com` auto-activates

---

## 🔑 Important Accounts

**Super Admin Email:** `batwiineltdgroup@gmail.com`
- Auto-activated
- All permissions
- Can manage other admins

---

## 📁 Files Added

```
batuma_gprs_weather/
├── app_simple.py                    ← Run this
├── user_management.py               ← User/role logic
├── frontend/
│   ├── login.html                   ← Login page
│   ├── dashboard.html               ← Admin panel
│   ├── app.js                       ← Updated with auth
│   └── index.html                   ← Updated with auth
└── AUTHENTICATION_GUIDE.md          ← Full docs
```

---

## 🚀 API Endpoints

### Public
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login user
- `GET /api/health` - Health check

### Admin Only
- `GET /api/admin/pending-approvals` - Pending accounts
- `POST /api/admin/approve-account` - Approve user
- `POST /api/admin/reject-account` - Reject user
- `GET /api/admin/users` - All users
- `POST /api/admin/set-user-role` - Change role (Super Admin only)
- `GET /api/admin/roles` - View all roles

---

## 🎯 Next Steps

1. **Test the system** (see above)
2. **Create Super Admin** with your email
3. **Invite users** to create accounts
4. **Review pending** accounts in admin panel
5. **Approve/Reject** as needed
6. **Manage roles** for team members

---

## ❓ Troubleshooting

### "Address already in use" error
```bash
# Kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :8000
kill -9 <PID>
```

### "Module not found" error
```bash
pip install flask flask-cors PyJWT waitress
```

### Can't access login page
- Check server is running
- Try http://localhost:8000/login.html
- Check console for errors (F12)

### Forgot Super Admin password
- Create new account with batwiineltdgroup@gmail.com email (different password)
- Old user data is in memory (resets on server restart)

---

## 💡 Tips

1. **Test Flow:** Create 3 accounts (1 super admin, 2 regular users)
2. **Admin Panel:** Show pending approvals first
3. **Roles:** Change a user's role to see the difference
4. **Logout:** Use logout button to test re-login flow
5. **Remember:** Super admin email is case-sensitive

---

**Ready to test?**

```bash
cd batuma_gprs_weather
python app_simple.py
```

Then open: http://localhost:8000/login.html

Happy testing! 🚀
