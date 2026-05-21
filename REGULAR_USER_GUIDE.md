# Regular User Access Guide

## User Roles & Capabilities

### User Types in Tap Trip

```
┌─────────────────────────────────────────────────────────────┐
│                    ROLE HIERARCHY                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  SUPER ADMIN                                                 │
│  └─ Batwiineltdgroup@gmail.com (Auto-activated)            │
│     └─ Full system access                                   │
│        └─ Manage all users, approve accounts                │
│           └─ View logs, system settings                     │
│                                                               │
│  ADMIN                                                        │
│  └─ Manually created or approved by Super Admin             │
│     └─ Approve regular user accounts                        │
│        └─ View transaction logs                             │
│           └─ Manage cards                                   │
│                                                               │
│  MODERATOR                                                    │
│  └─ Limited admin capabilities                              │
│     └─ View users                                           │
│        └─ Manage cards                                      │
│                                                               │
│  REGULAR USER ← YOU ARE HERE                                 │
│  └─ Full payment capabilities                               │
│     └─ Generate unlimited cards                             │
│        └─ Make payments with approvals                      │
│           └─ View own transactions                          │
│              └─ Add to digital wallets                      │
│
└─────────────────────────────────────────────────────────────┘
```

---

## How to Access as Regular User

### Step 1: Create Account

**URL:** `http://localhost:8000/login.html`

```
1. Click "Sign Up"
2. Enter Details:
   - Full Name: "John Doe"
   - Email: "john@example.com"
   - Phone: "+27123456789" (Your phone number)
   - Password: "SecurePass123!" (Min 8 chars, uppercase, number)
3. Click "Create Account"
```

### Step 2: Verify Account (2-Minute Window)

**Email Verification:**
```
1. Check email: john@example.com
2. Copy 6-digit code
3. Enter code in verification form
4. Timer: 2 minutes only ⏱️
5. Attempts: 3 maximum
Result: ✅ Account Active
```

**OR SMS Verification (Alternative):**
```
1. Click "Use SMS Instead"
2. Confirm phone: +27123456789
3. Check SMS message
4. Enter 6-digit code
5. Timer: 2 minutes only ⏱️
Result: ✅ Account Active
```

### Step 3: Login as Regular User

```
1. Go to: http://localhost:8000/login.html
2. Enter:
   - Email: john@example.com
   - Password: SecurePass123!
3. Click "Login"
Result: ✅ Redirected to Dashboard
```

---

## Regular User Features

### ✅ What You Can Do

#### 1. Virtual Card Management
```
✅ Generate unlimited virtual cards
✅ View all your cards
✅ See masked card numbers
✅ Track card balances
✅ View card history
✅ Delete unused cards (future feature)
```

#### 2. Payment Processing
```
✅ Make payments with 3 methods:
   ├─ Tap: NFC terminal
   ├─ QR Code: Merchant scans
   └─ NFC: Contactless
   
✅ Set daily spending limits (R1,000 - R10,000)
✅ View transaction limits
✅ Track daily spending
```

#### 3. Payment Approval
```
✅ Approve payments with biometric:
   ├─ Face Recognition
   ├─ Fingerprint
   └─ 6-Digit Code
   
✅ Decline suspicious transactions
✅ Set approval preferences
```

#### 4. Transaction History
```
✅ View all your transactions
✅ See merchant details
✅ Check transaction status
✅ Filter by date/amount
✅ Export transaction reports (future)
```

#### 5. Digital Wallets
```
✅ Add cards to Apple Wallet (iOS)
✅ Add cards to Google Wallet (Android)
✅ Use tap-to-pay at terminals
✅ Remove from wallet
```

#### 6. Account Management
```
✅ View profile information
✅ Update phone number
✅ Change password
✅ Set security preferences
✅ View login history
```

### ❌ What You CANNOT Do

```
❌ Approve other user accounts
❌ View other user's transactions
❌ Modify system settings
❌ Access admin dashboard
❌ View transaction logs for all users
❌ Create admin accounts
```

---

## ❌ What You CANNOT Access

### Admin-Only Features
```
❌ User management
   └─ Can't create/delete users
   └─ Can't change user roles
   
❌ System logs
   └─ Can't view audit logs
   └─ Can't see all transactions
   
❌ Settings
   └─ Can't change system settings
   └─ Can't adjust global limits
   
❌ Dashboard
   └─ Can't access admin panel
   └─ Can't see analytics
```

---

## Regular User Dashboard

### Main Interface
```
┌────────────────────────────────────────────────────────┐
│ 💳 Virtual Card & Payments                             │
├────────────────────────────────────────────────────────┤
│                                                          │
│ 📊 Your Virtual Cards                                   │
│ ├─ Card 1: My Shopping (Last 4: 5678)                 │
│ ├─ Card 2: Travel Card (Last 4: 1234)                 │
│ └─ [+ Generate New Card]                               │
│                                                          │
│ 💰 Make Payment                                         │
│ ├─ Select Card: [Dropdown]                             │
│ ├─ Merchant: [Text]                                    │
│ ├─ Amount: [Number]                                    │
│ ├─ Method: [Tap / QR / NFC]                            │
│ └─ [Proceed to Approval]                               │
│                                                          │
│ 🔐 Verify Payment                                       │
│ ├─ 👤 Face Recognition                                 │
│ ├─ 👆 Fingerprint                                      │
│ └─ 🔐 Code (6 Digits)                                  │
│                                                          │
│ 📲 Add to Wallet                                        │
│ ├─ Apple Pay (iOS)                                     │
│ └─ Google Pay (Android)                                │
│                                                          │
│ 📊 Transaction History                                  │
│ ├─ Payment 1: R250 - ABC Store (Completed)            │
│ ├─ Payment 2: R150 - XYZ Shop (Completed)             │
│ └─ [View More]                                         │
│                                                          │
│ ⚙️ Settings                                             │
│ ├─ Daily Limit: R2,000 (Adjust)                       │
│ ├─ Biometric Settings                                  │
│ └─ Notification Preferences                            │
│                                                          │
└────────────────────────────────────────────────────────┘
```

---

## Regular User Settings

### Daily Spending Limit

**How to Adjust:**
```
1. Go to: Settings
2. Find: Daily Limit
3. Current: R1,000 (default)
4. Adjust: Drag slider
5. Range: R1,000 - R10,000
6. Click: Save
7. Note: You are the owner - only you can change
```

**Example:**
```
Default:    R1,000/day
Adjusted:   R5,000/day  ← You set this
Maximum:    R10,000/day (hard limit)
```

### Biometric Settings

**Configure Approval Method:**
```
1. Settings → Biometric
2. Enable methods:
   ☑ Face Recognition
   ☑ Fingerprint
   ☑ 6-Digit Code
3. Set preferred method
4. Save preferences
```

### Notification Settings

```
SMS Notifications:
☑ Payment approved
☑ Payment declined
☑ Daily limit reached
☑ Suspicious activity

Email Notifications:
☑ Payment summary (daily)
☑ Security alerts
☑ Account changes
```

---

## API Access for Regular Users

### Available Endpoints

```
GET    /api/profile              # Your profile
GET    /api/cards                # Your cards
POST   /api/cards/generate       # Create card
GET    /api/cards/{id}/transactions  # Card history

POST   /api/payments/process     # Make payment
POST   /api/payments/{id}/approve    # Approve payment
POST   /api/payments/{id}/decline    # Decline payment

POST   /api/cards/{id}/apple-wallet      # Apple Wallet
POST   /api/cards/{id}/android-wallet    # Google Wallet

GET    /api/settings                 # Your settings
PUT    /api/settings/daily-limit      # Change daily limit
POST   /api/account/change-password   # Change password
```

### Example: Get Your Profile

```bash
curl http://localhost:8000/api/profile \
  -H "Authorization: Bearer YOUR_TOKEN"

Response:
{
  "user_id": "uuid-1234",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+27123456789",
  "role": "user",
  "status": "active",
  "account_verified": true,
  "cards_count": 2,
  "daily_limit": 5000,
  "daily_spent": 1250,
  "daily_remaining": 3750
}
```

### Example: Adjust Daily Limit

```bash
curl -X PUT http://localhost:8000/api/settings/daily-limit \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"daily_limit": 7500}'

Response:
{
  "success": true,
  "message": "Daily limit updated",
  "new_limit": 7500,
  "max_limit": 10000
}
```

---

## Regular User Workflow

### Complete Payment Flow

```
1. LOGIN (2-min verification)
   ↓
2. GENERATE CARD (or use existing)
   ↓
3. MAKE PAYMENT
   ├─ Select card
   ├─ Enter merchant & amount
   └─ Choose payment method
   ↓
4. APPROVE PAYMENT
   ├─ Choose biometric method
   ├─ Face/Fingerprint/Code
   └─ Verify identity
   ↓
5. SMS NOTIFICATION
   ├─ "Payment successful: R250 to ABC Store"
   ├─ Transaction ID: A1B2C3D4
   └─ Timestamp: 2026-01-17 10:30:00
   ↓
6. TRANSACTION SAVED
   ├─ Added to history
   ├─ Card balance updated
   └─ Daily limit decremented
   ↓
7. VIEW HISTORY
   ├─ Check all transactions
   └─ Export reports (future)
```

---

## Demo Accounts

### Super Admin (Full Access)
```
Email: batwiineltdgroup@gmail.com
Password: Likuwe@2023
Role: Super Admin
Verification: Instant (auto-approved)
Access: Everything
```

### Test Regular User
```
Email: user@example.com
Password: TestUser123!
Phone: +27791234567
Role: Regular User
Verification: 6-digit code (2 min)
Access: Payments, cards, wallets
```

---

## Common Tasks for Regular Users

### Generate New Card
```bash
POST /api/cards/generate
{
  "card_name": "Shopping Card"
}
```

### Make Payment
```bash
POST /api/payments/process
{
  "card_id": "uuid-1234",
  "amount": 250.50,
  "merchant_name": "ABC Store",
  "payment_method": "tap"
}
```

### Approve with Biometric
```bash
POST /api/approval/biometric-verify
{
  "approval_id": "ap-5678",
  "method": "face_recognition",
  "biometric_data": {}
}
```

### Add to Apple Wallet
```bash
POST /api/cards/{card_id}/apple-wallet
```

### View Transaction History
```bash
GET /api/cards/{card_id}/transactions?limit=10
```

---

## Limits & Constraints for Regular Users

| Constraint | Value | Notes |
|-----------|-------|-------|
| **Daily Limit** | R1,000 - R10,000 | You control (within range) |
| **Per Transaction** | R10,000 max | Hard limit |
| **Active Cards** | Unlimited | Create as many as needed |
| **Transactions/Day** | Unlimited | As long as daily limit allows |
| **Approval Timeout** | 10 minutes | Must approve within window |
| **Verification Code** | 2 minutes | Email/SMS code validity |
| **Verification Attempts** | 3 maximum | Then must resend code |

---

## Troubleshooting

### "Account Not Verified"
```
Check: Email/SMS for 6-digit code
Timer: Only 2 minutes to verify
Solution: Request code resend
```

### "Daily Limit Exceeded"
```
Current Spent: R9,500
Daily Limit: R10,000
Remaining: R500
Solution: Wait for midnight reset or increase limit
```

### "Payment Approval Timeout"
```
Initiated: 10:00 AM
Timeout: 10:10 AM (exactly 10 min)
Solution: Initiate new payment
```

### "Biometric Failed"
```
Tried: Face Recognition - failed
Fallback: Use 6-digit code
Solution: Code always works as backup
```

---

## Security Tips for Regular Users

✅ **DO:**
- Use strong passwords (uppercase + numbers)
- Enable biometric for payments
- Set appropriate daily limits
- Check transaction history regularly
- Update phone if it changes
- Logout from shared devices

❌ **DON'T:**
- Share approval codes
- Use same password on other sites
- Accept payment over unsecured WiFi
- Click suspicious links
- Share card numbers
- Store codes on paper

---

## Support Resources

For help as a regular user:

1. **Payment Issues**
   - Check daily limit hasn't been exceeded
   - Ensure 2-minute verification window
   - Try different approval method

2. **Access Issues**
   - Clear browser cache
   - Check internet connection
   - Try different browser

3. **Biometric Issues**
   - Use backup 6-digit code
   - Update device biometric data
   - Check device compatibility

4. **Account Issues**
   - Check email for verification code
   - Ensure phone number is correct
   - Contact support for lockout

---

**Now You Know:**
- ✅ How to access as regular user
- ✅ What you can do
- ✅ Your payment limits
- ✅ How to adjust daily limits
- ✅ All available features

**Start using Tap Trip as a regular user today!**
