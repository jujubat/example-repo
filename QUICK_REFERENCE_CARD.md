# Phase 5 - Quick Reference Card

**Print this and keep nearby!**

---

## 🎯 What's New in Phase 5

| Feature | Before | After |
|---------|--------|-------|
| Verification | 10 min | **2 min** ✅ |
| Password Toggle | 👁️ Icon | **☑️ Checkbox** ✅ |
| Daily Limit | R5,000 | **R1,000 default** ✅ |
| Max Daily Limit | No max | **R10,000** ✅ |
| Payment Methods | None | **Tap/QR/NFC** ✅ |
| Biometric | None | **Face/Fingerprint/Code** ✅ |
| Wallets | None | **Apple/Google Pay** ✅ |
| User Guide | None | **1000+ lines** ✅ |
| Approval System | None | **10-min workflow** ✅ |
| Production Guide | None | **2000+ lines** ✅ |

---

## 📱 User Workflow

### Signup → Login → Payment (3 Steps)

```
STEP 1: SIGNUP
┌─────────────────────────────────────┐
│ Email: user@example.com             │
│ Password: SecurePass123!            │
│ Phone: +27791234567                 │
│ [Create Account]                    │
└─────────────────────────────────────┘
        ↓
VERIFY (2 MINUTES ⏱️)
┌─────────────────────────────────────┐
│ Check email for 6-digit code        │
│ Enter code: 123456                  │
│ Time remaining: 1:45                │
│ [Verify]                            │
└─────────────────────────────────────┘
        ↓
STEP 2: LOGIN
┌─────────────────────────────────────┐
│ Email: user@example.com             │
│ Password: ☑ SecurePass123!          │ ← Checkbox!
│ [Login]                             │
└─────────────────────────────────────┘
        ↓
DASHBOARD
├─ Generate Card (R1,000 limit)
├─ View Cards
├─ Make Payment
└─ Adjust Daily Limit (R1,000-R10,000)
        ↓
STEP 3: PAYMENT
┌─────────────────────────────────────┐
│ Card: My Shopping Card              │
│ Merchant: ABC Store                 │
│ Amount: R250                         │
│ Method: [Tap] [QR] [NFC]           │
│ [Process Payment]                   │
└─────────────────────────────────────┘
        ↓
BIOMETRIC APPROVAL (10 MIN WINDOW)
┌─────────────────────────────────────┐
│ Choose approval method:             │
│ [👤 Face] [👆 Fingerprint] [🔐 Code] │
│ Verify: ▓▓▓▓▓▓▓▓▓▓ (2 sec)          │
│ Status: ✓ Approved                  │
└─────────────────────────────────────┘
        ↓
SMS NOTIFICATION
✓ Payment successful: R250 to ABC Store
  Ref: A1B2C3D4
  Time: 2026-01-17 10:30:00
```

---

## 💾 API Endpoints (16 Total)

### Card Management
```
POST   /api/cards/generate              Create card (R1,000 limit)
GET    /api/cards                       List cards
POST   /api/cards/{id}/daily-limit      Adjust limit (R1,000-R10,000)
POST   /api/cards/{id}/apple-wallet     Add to Apple Wallet
POST   /api/cards/{id}/android-wallet   Add to Google Wallet
GET    /api/cards/{id}/transactions     Get history
```

### Payment Processing
```
POST   /api/payments/process            Make payment
POST   /api/payments/{id}/approve       Approve payment
POST   /api/payments/{id}/decline       Decline payment
GET    /api/payments/history            View history
```

### Approval System
```
POST   /api/approval/initiate           Start approval (10 min)
GET    /api/approval/{id}/status        Check status
POST   /api/approval/biometric-verify   Biometric approval
```

### Notifications
```
POST   /api/qrcode/generate             Generate QR code
POST   /api/notifications/send-sms      Send SMS
POST   /api/approval-code/set           Set 6-digit code
```

---

## 🔒 Security Features

| Feature | Details |
|---------|---------|
| **Verification Code** | 2 min expiry, 3 attempts max |
| **Approval Window** | 10 minutes, then expires |
| **Daily Limit** | R1,000 min - R10,000 max |
| **Biometric** | Face/Fingerprint/Code (backup) |
| **Card Numbers** | Masked (****-****-****-1234) |
| **SMS Alerts** | All payments confirmed |
| **JWT Tokens** | 24-hour expiry |

---

## 📊 Daily Limits Guide

```
Default Daily Limit:        R1,000
Minimum:                    R1,000
Maximum:                    R10,000
Per-Transaction Limit:      R10,000
Daily Reset:                Midnight
User Can Adjust:            Yes
Owner Only:                 Yes
Adjustable Range:           R100 increments
```

**Example:**
```
Started with R1,000
Spent R250 on payment
Remaining for day: R750

User adjusts to R5,000
New daily limit: R5,000
Remaining: R4,750
```

---

## 🎮 Quick Commands (curl)

### Generate Card
```bash
curl -X POST http://localhost:8000/api/cards/generate \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"card_name": "My Card"}'
```

### Make Payment
```bash
curl -X POST http://localhost:8000/api/payments/process \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "card_id": "uuid",
    "amount": 250,
    "merchant_name": "ABC Store",
    "payment_method": "tap"
  }'
```

### Adjust Daily Limit
```bash
curl -X POST http://localhost:8000/api/cards/{id}/daily-limit \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_limit": 5000}'
```

---

## 📚 Documentation Map

```
START HERE
    ↓
PHASE_5_QUICK_START.md (5 min)
    ↓
CHOOSE YOUR PATH:
    ├─ User? → REGULAR_USER_GUIDE.md (1000 lines)
    ├─ Developer? → PHASE_5_QUICK_REFERENCE.md (250 lines)
    ├─ DevOps? → PRODUCTION_SETUP_GUIDE.md (2000 lines)
    ├─ Tech Deep? → PHASE_5_VIRTUAL_CARDS_COMPLETE.md (400 lines)
    └─ Lost? → PHASE_5_DOCUMENTATION_INDEX.md
```

---

## ⚡ Common Tasks

### Generate Card
```
1. Login
2. Click "Generate Card"
3. Name: "Shopping Card"
4. Daily Limit: R1,000 (default)
5. Click Generate
6. Card appears in grid
```

### Make Payment
```
1. Select card from dropdown
2. Enter merchant name
3. Enter amount (max R10,000)
4. Choose method (tap/QR/NFC)
5. Click "Process Payment"
6. Choose biometric
7. Approve (face/fingerprint/code)
8. SMS confirmation
```

### Adjust Daily Limit
```
1. Click Settings
2. Find "Daily Limit"
3. Move slider (R1,000-R10,000)
4. Click Save
5. Limit updated
6. SMS confirmation
```

### Add to Apple Wallet
```
1. Select card
2. Click "Add to Apple Wallet"
3. Phone triggers Wallet app
4. Card appears in wallet
5. Use tap-to-pay
```

---

## 🚀 Demo Accounts

### Super Admin
```
Email: batwiineltdgroup@gmail.com
Password: Likuwe@2023
Role: Super Admin
Access: EVERYTHING
```

### Regular User
```
Email: user@example.com
Password: TestUser123!
Phone: +27791234567
Role: User
Access: Payments, cards, wallets
```

---

## ⚙️ Limits & Constraints

| Constraint | Value | Notes |
|-----------|-------|-------|
| Daily Limit Min | R1,000 | Default starting limit |
| Daily Limit Max | R10,000 | Cannot exceed |
| Per Transaction | R10,000 | Hard limit |
| Verification Code | 2 min | Email/SMS |
| Code Attempts | 3 | Then resend |
| Approval Window | 10 min | Must approve |
| JWT Token | 24 hrs | Auto-refresh |
| Cards | Unlimited | Create as many |

---

## 🔧 Environment Variables

```
# Required
FLASK_APP=app_simple.py
JWT_SECRET_KEY=your_secret_key_here

# Optional - SMS (Development)
SMS_SERVICE=mock

# Optional - SMS (Production)
SMS_SERVICE=twilio
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...

# Optional - Database
DATABASE_URL=postgresql://user:pass@localhost/tap_trip
MONGODB_URL=mongodb://localhost:27017/tap_trip
```

---

## 🐛 Troubleshooting

### "Verification Code Expired"
→ Only 2 minutes! Click "Resend Code"

### "Daily Limit Exceeded"
→ Wait for midnight reset OR increase limit

### "Approval Timeout"
→ Window is 10 minutes. Start new payment.

### "Biometric Failed"
→ Use 6-digit code as backup

### "Can't Login"
→ Check email verified first

### "Card Not Linked"
→ Ensure Wallet app installed

---

## 📞 File Locations

All files in: `Batuma_full_app/`

```
Core App:
  ├─ app_simple.py
  └─ user_management.py

Frontend:
  └─ frontend/
      ├─ login.html
      ├─ payments.html
      └─ styles.css

Documentation:
  ├─ PHASE_5_QUICK_START.md ← Start here!
  ├─ REGULAR_USER_GUIDE.md
  ├─ PRODUCTION_SETUP_GUIDE.md
  └─ (5 more docs)
```

---

## ✨ Key Changes This Phase

```
✅ Verification: 10 min → 2 min
✅ Password UI: Eye icon → Checkbox
✅ Daily Limit: R5,000 → R1,000 (adjustable to R10,000)
✅ Approval: New 10-min workflow
✅ Biometric: 3 methods (face/fingerprint/code)
✅ Payment: 3 methods (tap/QR/NFC)
✅ Wallets: Apple Pay & Google Pay
✅ SMS: All payments confirmed
✅ Documentation: 5,500+ lines added
✅ Production Ready: Deployment guide included
```

---

## 🎯 Your Next Steps

1. **Try It Out**
   → Run: `python app_simple.py`
   → Visit: `http://localhost:8000/login.html`

2. **Create Demo Account**
   → Use "Sign Up" form
   → Verify with 2-min code

3. **Generate Card**
   → R1,000 limit (default)

4. **Make Payment**
   → Approve with face/fingerprint/code
   → Get SMS notification

5. **Adjust Limit**
   → Settings → Daily Limit
   → Move slider to R5,000
   → Save

---

**Phase 5: 100% Complete ✅**

**All 10 features implemented and documented**

**Ready for production deployment!** 🚀

---

*For detailed help, see PHASE_5_DOCUMENTATION_INDEX.md*
