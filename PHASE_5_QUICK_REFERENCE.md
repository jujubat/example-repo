# Phase 5: Virtual Card System - Quick Reference

## Quick Start - Virtual Card System

### 1. Access Payment Dashboard
```
URL: http://localhost:8000/payments.html
Requires: Valid authentication token
```

### 2. Generate Virtual Card
```bash
# Frontend
Click: "+ Generate New Card"
Enter: Card Name (e.g., "My Shopping Card")
Result: Card with last 4 digits displayed

# API
POST /api/cards/generate
Body: { "card_name": "My Card" }
Response: { "card_id": "uuid-1234", "last_four": "5678" }
```

### 3. Make Payment
```bash
# Steps
1. Select Card from dropdown
2. Enter Merchant Name
3. Enter Amount
4. Choose Payment Method (Tap, QR Code, NFC)
5. Click "Proceed to Approval"

# API
POST /api/payments/process
Body: {
    "card_id": "uuid-1234",
    "amount": 99.99,
    "merchant_name": "ABC Store",
    "payment_method": "tap"
}
```

### 4. Approve Payment (Biometric)

**Option 1: Face Recognition**
```bash
Click: "👤 Face Recognition"
Allow: Camera access
Perform: Face scan
Result: Biometric verified
```

**Option 2: Fingerprint**
```bash
Click: "👆 Fingerprint"
Action: Place finger on device scanner
Result: Biometric verified
```

**Option 3: 6-Digit Code**
```bash
Click: "🔐 Code (6 Digits)"
Enter: Your approval code (6 numeric digits)
Result: Code verified
```

### 5. Complete & Receive SMS
```bash
Click: "Approve & Pay"
Result: 
  ✅ Payment processed
  📱 SMS notification sent
  📊 Transaction in history
```

### 6. Add to Digital Wallet

**Apple Wallet (iOS):**
```
1. Click card → "Apple Pay"
2. Allow adding pass
3. Open Wallet app → Card appears
4. Use at compatible terminals
```

**Google Wallet (Android):**
```
1. Click card → "Google Pay"
2. Allow adding pass  
3. Open Google Wallet → Card appears
4. Use at compatible terminals
```

---

## Key Changes from Phase 4

| Feature | Phase 4 | Phase 5 |
|---------|---------|---------|
| Verification Code Duration | 10 minutes | **2 minutes** |
| Password Toggle | 👁️ Eye icon | **☐ Checkbox** |
| Approval Methods | Email/SMS only | **Biometric + Code** |
| Payment Methods | None | **Tap, QR, NFC** |
| Digital Wallets | Not supported | **Apple + Google** |
| SMS Notifications | Email only | **All payments** |
| Transaction History | Not available | **Full tracking** |

---

## Verification Code System

### New 2-Minute Timer
```
Signup/Email Sent
    ↓
Timer Starts: 2 minutes
    ↓
Enter Code (within 2 min) → Success ✅
    OR
Wait > 2 minutes → Code Expired ❌ (Resend required)
```

### 3-Attempt Limit
```
Failed Attempt 1 → "2 attempts remaining"
Failed Attempt 2 → "1 attempt remaining"
Failed Attempt 3 → Code Expired ❌ (Resend)
```

### API Endpoints
```
POST /api/auth/send-verification-email     # Send email code
POST /api/auth/verify-email                # Verify email code
POST /api/auth/send-sms-code               # Send SMS code
POST /api/auth/verify-sms                  # Verify SMS code
```

---

## Password Visibility Checkbox

### Design Update
```
BEFORE:  [Password field]  👁️
AFTER:   [Password field]  ☐ Show Password
```

### Features
- Accessible checkbox design
- Clear "Show Password" label
- Mobile-friendly (44x44px tap target)
- Consistent styling across all forms

### Usage
```html
<input type="password" id="pwd">
<label class="password-checkbox-label">
    <input type="checkbox" onchange="togglePasswordVisibility('pwd', this)">
    <span>Show Password</span>
</label>
```

---

## Virtual Card System

### Card Generation

**Automatic Card Details:**
- Card Number: 16 digits (masked as ****-****-****-5678)
- CVV: 3-digit security code
- Expiry: 5 years from creation
- Status: Active immediately

**Limits per Card:**
- Transaction Limit: $10,000 max per transaction
- Daily Limit: $5,000 max per day
- Balance: Tracks cumulative transactions

### Card Storage
```python
{
    'card_id': 'uuid-1234',
    'card_name': 'My Card',
    'card_number': '1234567890123456',
    'last_four': '5678',
    'expiry_month': 1,
    'expiry_year': 2027,
    'balance': 1000.00,
    'daily_spent': 250.00,
    'apple_wallet_linked': False,
    'android_wallet_linked': False,
    'transactions': [...]
}
```

---

## Payment Methods

### 1. Tap (NFC)
- **How:** Customer taps card at terminal
- **Speed:** 1-2 seconds
- **Security:** High (encrypted)
- **Best for:** In-store purchases

### 2. QR Code
- **How:** Generate QR → Merchant scans → Confirm
- **Speed:** 5-10 seconds
- **Security:** Medium (one-time code)
- **Best for:** Online/contactless purchases

### 3. NFC (Contactless)
- **How:** Wave card near terminal
- **Speed:** 1-2 seconds
- **Security:** High (encrypted)
- **Best for:** Quick payments at compatible terminals

---

## Biometric Approval Methods

### Face Recognition
```
Requirements:
  - Front-facing camera
  - Good lighting
  - Face clearly visible
  
Process:
  1. Click "Face Recognition"
  2. Allow camera access
  3. Position face in frame
  4. System captures & verifies
  5. Auto-approves if match found
  
Fallback: Use 6-digit code if failed
```

### Fingerprint
```
Requirements:
  - Device with fingerprint sensor
  - Clean finger
  - Enrolled fingerprint

Process:
  1. Click "Fingerprint"
  2. Place finger on sensor
  3. System reads & verifies
  4. Auto-approves if match found

Fallback: Use 6-digit code if failed
```

### 6-Digit Code Password
```
Setup:
  1. API: POST /api/approval-code/set
  2. Body: { "code": "123456" }
  3. Must be 6 numeric digits

Usage:
  1. Click "Code (6 Digits)"
  2. Enter your 6-digit code
  3. System verifies immediately
  4. Always available as fallback
```

---

## SMS Payment Notifications

### When Sent
- ✅ Payment approved
- ❌ Payment declined
- ⚠️ Daily limit exceeded
- ⚠️ Transaction limit exceeded

### Message Content
```
Payment successful: $99.99 transferred to ABC Store.
Transaction ID: A1B2C3D4.
Date: 2026-01-17 10:30:00
```

### Integration (Production)
```python
# Currently: Mock (prints to console)
# Production options:
#   - Twilio SMS API
#   - AWS SNS (Simple Notification Service)
#   - Firebase Cloud Messaging
#   - Vonage (Nexmo)
```

---

## API Quick Reference

### Virtual Cards
```bash
GET /api/cards                           # List all cards
POST /api/cards/generate                 # Create new card
POST /api/cards/{id}/apple-wallet        # Add to Apple Wallet
POST /api/cards/{id}/android-wallet      # Add to Google Wallet
GET /api/cards/{id}/transactions         # Transaction history
```

### Payments
```bash
POST /api/payments/process               # Initiate payment
POST /api/payments/{id}/approve          # Approve payment
POST /api/payments/{id}/decline          # Decline payment
GET /api/payments/{id}/status            # Check status
```

### Approvals
```bash
POST /api/approval/initiate              # Start approval
POST /api/approval/biometric-verify      # Submit biometric
GET /api/approval/{id}/status            # Check status
POST /api/approval-code/set              # Set 6-digit code
```

---

## Approval Workflow Timeline

```
Payment Initiated
    ↓
Approval Request Created (10-min timeout)
    ↓ Choose method:
    ├─ Face → Scan → Verified (< 2 sec)
    ├─ Fingerprint → Scan → Verified (< 2 sec)
    └─ Code → Enter → Verified (< 5 sec)
    ↓
Payment Approved ✅
    ↓
SMS Sent to User
    ↓
Transaction Complete
    ↓
Added to History
```

---

## Transaction History

### View Transactions
```
Frontend: Payment Dashboard → Transaction History section
API: GET /api/cards/{card_id}/transactions?limit=10
```

### Transaction Details
```
- Transaction ID
- Amount
- Merchant Name
- Payment Method (tap, qr_code, nfc)
- Status (completed, pending, declined)
- Timestamp
```

---

## Card Limits & Constraints

| Constraint | Value | Notes |
|-----------|-------|-------|
| Transaction Max | $10,000 | Per transaction |
| Daily Max | $5,000 | Resets at midnight |
| Card Number | 16 digits | Standard format |
| CVV | 3 digits | Always masked |
| Expiry | 5 years | From creation |
| Active Cards | Unlimited | Per user |
| Daily Attempts | Unlimited* | *After limit reset |
| Approval Timeout | 10 minutes | Auto-decline if expired |
| Code Length | 6 digits | Numeric only |
| Verification Duration | 2 minutes | Email & SMS |

---

## Common curl Commands

### Generate Card
```bash
curl -X POST http://localhost:8000/api/cards/generate \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"card_name":"Shopping Card"}'
```

### List Cards
```bash
curl http://localhost:8000/api/cards \
  -H "Authorization: Bearer TOKEN"
```

### Process Payment
```bash
curl -X POST http://localhost:8000/api/payments/process \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "card_id":"uuid",
    "amount":50,
    "merchant_name":"Store",
    "payment_method":"tap"
  }'
```

### Approve Payment
```bash
curl -X POST http://localhost:8000/api/payments/APPROVAL_ID/approve \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"biometric_verified":true}'
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Code expired immediately | 2-minute window only; resend if needed |
| Card not appearing | Refresh page or generate new card |
| Biometric fails | Try different method or use code password |
| Approval times out | Must complete within 10 minutes |
| SMS not received | Verify phone number format |
| Payment limit exceeded | Wait for daily reset at midnight |
| Wallet add fails | Check device compatibility (iOS/Android) |

---

## Browser Support

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Payments | ✅ | ✅ | ✅ | ✅ |
| Biometric* | ✅ | ✅ | ✅ | ✅ |
| Wallet | ✅ | ✅ | ✅ | ✅ |
| QR Display | ✅ | ✅ | ✅ | ✅ |

*Biometric requires HTTPS in production

---

## Files Modified/Created

| File | Status | Purpose |
|------|--------|---------|
| `frontend/payments.html` | NEW | Payment interface |
| `user_management.py` | UPDATED | Card/payment backend |
| `app_simple.py` | UPDATED | API endpoints |
| `frontend/login.html` | UPDATED | Password checkbox |
| `frontend/styles.css` | UPDATED | Checkbox styling |

---

## Next Steps

1. **Setup Approval Code**
   ```bash
   POST /api/approval-code/set
   Body: {"code": "123456"}
   ```

2. **Generate Your Card**
   ```
   Click: "+ Generate New Card"
   Enter: Name
   ```

3. **Make First Payment**
   ```
   Select Card → Amount → Method → Approve
   ```

4. **Check SMS Confirmation**
   ```
   Monitor: Your phone SMS inbox
   ```

5. **Add to Wallet**
   ```
   Click: Apple Pay or Google Pay
   Confirm: Add to wallet
   ```

---

## For Complete Documentation
See: `PHASE_5_VIRTUAL_CARDS_COMPLETE.md`

### 1. Initialize Systems

```python
from batuma_gprs_weather.analytics.transaction_analytics import TransactionAnalyticsEngine
from batuma_gprs_weather.payment.virtual_card_system import VirtualCardSystem
from batuma_gprs_weather.auth.kyc_verification import KYCVerificationSystem
from batuma_gprs_weather.auth.biometric_auth import BiometricAuthenticationSystem
from batuma_gprs_weather.financial.banking_integration import BankingIntegrationSystem
from batuma_gprs_weather.fleet.fleet_management_scale import FleetManagementAtScale

analytics = TransactionAnalyticsEngine()
cards = VirtualCardSystem()
kyc = KYCVerificationSystem()
biometric = BiometricAuthenticationSystem()
banking = BankingIntegrationSystem()
fleet = FleetManagementAtScale()
```

### 2. Flask Setup

```python
from flask import Flask
from batuma_gprs_weather.routes.financial_routes import financial_bp

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

app.register_blueprint(financial_bp)

if __name__ == '__main__':
    app.run(debug=False, port=5000)
```

### 3. Create User Account

```python
# Create virtual card
card = cards.create_card("27123456789", "John Doe")
print(f"Card: {card.account_number}")

# Create KYC profile
kyc_profile = kyc.create_kyc_profile("27123456789", "John Doe")
```

---

## API Quick Reference

### Virtual Cards

```bash
# Create card
curl -X POST http://localhost:5000/api/financial/cards/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "phone_number": "27123456789",
    "customer_name": "John Doe"
  }'

# Get balance
curl -X GET http://localhost:5000/api/financial/cards/27123456789/balance \
  -H "Authorization: Bearer TOKEN"

# Load money
curl -X POST http://localhost:5000/api/financial/cards/27123456789/load-money \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "amount": 500,
    "source": "bank"
  }'

# Get transactions
curl -X GET http://localhost:5000/api/financial/cards/27123456789/transactions?limit=50 \
  -H "Authorization: Bearer TOKEN"
```

### Transfers

```bash
# Phone to phone transfer
curl -X POST http://localhost:5000/api/financial/transfers/phone-to-phone \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "from_phone": "27123456789",
    "to_phone": "27987654321",
    "amount": 100
  }'

# Transfer to bank
curl -X POST http://localhost:5000/api/financial/transfers/to-bank \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "from_phone": "27123456789",
    "to_account": "1234567890",
    "to_bank": "Absa",
    "amount": 1000
  }'

# Verify transfer
curl -X POST http://localhost:5000/api/financial/transfers/TRF_123/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "verification_code": "123456"
  }'
```

### KYC Verification

```bash
# Create profile
curl -X POST http://localhost:5000/api/financial/kyc/profile/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "phone_number": "27123456789",
    "customer_name": "John Doe",
    "email": "john@example.com"
  }'

# Upload document
curl -X POST http://localhost:5000/api/financial/kyc/27123456789/upload-document \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@id.pdf" \
  -F "document_type=id_card"

# Upload photo
curl -X POST http://localhost:5000/api/financial/kyc/27123456789/upload-photo \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@photo.jpg"

# Get KYC status
curl -X GET http://localhost:5000/api/financial/kyc/27123456789/status \
  -H "Authorization: Bearer TOKEN"
```

### Biometric Authentication

```bash
# Enroll biometric
curl -X POST http://localhost:5000/api/financial/biometric/enroll \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "phone_number": "27123456789",
    "biometric_type": "face_recognition"
  }'

# Authenticate with biometric
curl -X POST http://localhost:5000/api/financial/biometric/authenticate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "phone_number": "27123456789",
    "biometric_type": "face_recognition",
    "biometric_data": "BASE64_ENCODED_FACE_DATA"
  }'

# Set passcode
curl -X POST http://localhost:5000/api/financial/passcode/set \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "phone_number": "27123456789",
    "passcode": "123456"
  }'
```

### Banking

```bash
# Link bank account
curl -X POST http://localhost:5000/api/financial/banking/link-account \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "phone_number": "27123456789",
    "bank_name": "Absa",
    "account_number": "1234567890",
    "branch_code": "001001",
    "account_holder": "John Doe",
    "account_type": "cheque"
  }'
```

---

## Common Code Patterns

### Pattern 1: Create User & Load Money

```python
# Create card
card = cards.create_card("27123456789", "John Doe")

# Load money from bank
success = cards.load_money_from_bank(
    "27123456789",
    500.0,
    "FNB",
    "1234567890"
)

# Check balance
balance = card.get_balance()
print(f"Balance: R{balance}")
```

### Pattern 2: Complete Transfer Workflow

```python
# Transfer phone-to-phone
transfer = cards.transfer_phone_to_phone(
    "27123456789",
    "27987654321",
    100.0
)

if transfer:
    print(f"Transfer: {transfer.reference_number}")
    print(f"Status: {transfer.status}")
    print(f"Fee: R{transfer.fee_rands}")
else:
    print("Transfer failed")
```

### Pattern 3: KYC Verification Workflow

```python
import base64

# Create profile
profile = kyc.create_kyc_profile("27123456789", "John Doe")

# Upload document
with open("id.pdf", "rb") as f:
    doc_data = base64.b64encode(f.read()).decode()
    doc = kyc.upload_document("27123456789", "id_card", doc_data, "id.pdf")

# Upload photo
with open("photo.jpg", "rb") as f:
    photo_data = base64.b64encode(f.read()).decode()
    photo = kyc.upload_photo("27123456789", photo_data)

# Verify document (after OCR processing)
kyc.verify_document("27123456789", doc.doc_id, 
    {"number": "1234567890", "name": "John Doe"}, 
    verified_by="agent_001"
)

# Verify face
kyc.verify_face_recognition("27123456789", photo.photo_id, match_score=0.92)

# Approve KYC
kyc.approve_kyc("27123456789", "agent_001", "All verified")

# Check status
status = kyc.get_verification_status("27123456789")
print(f"Verified: {status['is_verified']}")
```

### Pattern 4: Biometric Authentication for Transaction

```python
# Enroll face recognition
face_enrollment = biometric.enroll_biometric("27123456789", "face_recognition")
biometric.add_biometric_sample("27123456789", "face_recognition", face_data_1)
biometric.add_biometric_sample("27123456789", "face_recognition", face_data_2)
biometric.add_biometric_sample("27123456789", "face_recognition", face_data_3)

# Set passcode
biometric.set_passcode("27123456789", "123456")

# Later: Verify high-value transaction (R8000)
auth_data = {
    "face_recognition": captured_face_data,
    "passcode": "123456"
}

verified = biometric.verify_transaction("27123456789", 8000.0, auth_data)

if verified:
    # Process transfer
    transfer = cards.transfer_to_bank("27123456789", "1234567890", "Absa", 8000)
else:
    print("Authentication failed")
```

### Pattern 5: Fleet Bulk Import

```python
import csv

# Read buses from CSV
buses_data = []
with open("buses.csv") as f:
    reader = csv.DictReader(f)
    buses_data = list(reader)

# Bulk add buses
added, errors = fleet.bulk_add_buses(buses_data)
print(f"Added {added} buses, {errors} errors")

# Read routes from CSV
routes_data = []
with open("routes.csv") as f:
    reader = csv.DictReader(f)
    routes_data = list(reader)

# Bulk add routes
added, errors = fleet.bulk_add_routes(routes_data)
print(f"Added {added} routes, {errors} errors")

# Add stops to each route
for route_data in routes_data:
    route = fleet.get_route_by_number(route_data['route_number'])
    if route:
        # Read stops for this route
        stops = [...]  # Load from data
        fleet.add_stops_to_route(route.route_id, stops)

# Get summary
summary = fleet.get_fleet_summary()
print(f"Total buses: {summary['total_buses']}")
print(f"Total routes: {fleet.get_routes_summary()['total_routes']}")
```

### Pattern 6: Transaction Analytics

```python
from batuma_gprs_weather.analytics.transaction_analytics import (
    Transaction, AnalyticsFilter, TimeGranularity
)

# Add transactions
for _ in range(100):
    txn = Transaction(
        f"TXN_{_}", "ticket", "CLIENT_1", "ROUTE_1", 50.0
    )
    analytics.add_transaction(txn)

# Get analytics
# Daily breakdown
daily = analytics.get_daily_breakdown()
print(f"Daily revenue: R{daily.total_amount}")

# Client statistics
client_stats = analytics.get_client_statistics("CLIENT_1")
print(f"Client revenue: R{client_stats['total_revenue']}")

# Route comparison
routes_compare = analytics.get_route_comparison(["ROUTE_1", "ROUTE_2"])
print(f"Route 1 vs Route 2: {routes_compare}")

# Dashboard data
dashboard = analytics.get_dashboard_data()
print(f"Dashboard: {dashboard}")

# Export report
report = analytics.export_report(TimeGranularity.MONTHLY)
print(f"Report exported: {report}")
```

---

## Data Models Quick Reference

### Virtual Card

```python
{
    'card_id': 'CARD_123',
    'account_number': '10123456789',
    'phone_number': '27123456789',
    'status': 'active',
    'balance': 1500.00,
    'daily_limit': 5000.00,
    'daily_spent': 250.00,
    'created_at': '2026-01-16T10:00:00Z'
}
```

### Money Transfer

```python
{
    'transfer_id': 'TRF_123',
    'from_phone': '27123456789',
    'to_phone': '27987654321',
    'amount': 100.00,
    'fee': 1.50,
    'status': 'completed',
    'reference': 'REF_123',
    'created_at': '2026-01-16T10:00:00Z',
    'completed_at': '2026-01-16T10:00:15Z'
}
```

### KYC Profile

```python
{
    'phone_number': '27123456789',
    'customer_name': 'John Doe',
    'kyc_level': 3,
    'verification_status': 'approved',
    'is_active': True,
    'created_at': '2026-01-16T09:00:00Z',
    'approved_at': '2026-01-16T10:00:00Z',
    'expires_at': '2027-01-16T10:00:00Z'
}
```

### Biometric Profile

```python
{
    'phone_number': '27123456789',
    'biometrics': {
        'face_recognition': {
            'is_enrolled': True,
            'is_enabled': True,
            'verify_attempts': 5,
            'failed_attempts': 0
        },
        'fingerprint': {
            'is_enrolled': False,
            'is_enabled': False
        }
    },
    'passcode': {
        'is_set': True,
        'is_locked': False,
        'used_count': 12
    }
}
```

### Bank Account

```python
{
    'account_id': 'BA_123',
    'bank_name': 'Absa',
    'account_number': '****7890',
    'branch_code': '001001',
    'account_type': 'cheque',
    'verification_status': 'verified',
    'is_primary': True,
    'linked_at': '2026-01-16T10:00:00Z',
    'verified_at': '2026-01-16T10:15:00Z'
}
```

### Bus

```python
{
    'bus_id': 'BUS_123',
    'registration': 'GP99ABC',
    'bus_type': 'local',
    'capacity': 50,
    'status': 'operational',
    'current_route': 'ROUTE_101',
    'location': {
        'latitude': -26.1919,
        'longitude': 28.2410,
        'timestamp': '2026-01-16T10:00:00Z'
    },
    'total_kilometers': 1250.50,
    'total_trips': 45,
    'passengers_today': 250,
    'revenue_today': 1250.00
}
```

### Route

```python
{
    'route_id': 'ROUTE_123',
    'route_number': '101',
    'start_location': 'Johannesburg',
    'end_location': 'Pretoria',
    'status': 'active',
    'distance_km': 60.0,
    'stops_count': 12,
    'train_stations': 2,
    'assigned_buses': 5,
    'daily_passengers': 500,
    'daily_revenue': 2500.00
}
```

---

## Error Codes

```
200 - Success
201 - Created
400 - Bad request
401 - Unauthorized
403 - Forbidden
404 - Not found
429 - Rate limit exceeded
500 - Internal server error

Financial-specific:
4001 - Insufficient balance
4002 - Daily limit exceeded
4003 - Invalid account details
4004 - Account not verified
4005 - Transaction locked
4006 - KYC required
4007 - Biometric enrollment required
```

---

## Performance Tips

1. **Cache Analytics Results** (5 minutes)
   - Use `TransactionAnalyticsEngine` caching
   - Avoid repeated queries for same filters

2. **Bulk Operations**
   - Use `bulk_add_buses()` instead of loop
   - Use `bulk_add_routes()` instead of loop

3. **Rate Limiting**
   - Respect 1000 requests/hour limit
   - Implement retry logic with backoff

4. **Database Queries**
   - Use indexed fields (phone_number, account_number, route_number)
   - Limit result sets

5. **Real-time Updates**
   - Use WebSockets for GPS tracking
   - Batch analytics updates

---

## Limits & Constraints

```
Virtual Cards:
- Daily transfer limit: R50,000
- Single transfer limit: R10,000
- Max bank accounts per user: 5
- Account balance limit: Unlimited

Transactions:
- Minimum: R0.01 (transfers), R10+ (most)
- Maximum: R10,000 (transfers), R50,000 (daily)
- Processing: 1-2 hours (bank), instant (P2P)

KYC:
- Document size: Max 10MB
- Verification: Within 24 hours
- Expiry: 365 days
- Re-verification: 30 days before expiry

Biometric:
- Enrollment samples: 3 required
- Match threshold: 80% (0.8)
- Passcode: 6 digits only
- Failed attempts: 3 × 15-min lockout

Fleet:
- Buses per route: 10 max
- Stops per route: 50 max
- Routes: 100,000+ supported
- Buses: 1,000+ supported
```

---

## Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1672502400
```

When rate limited (429 response):

```json
{
    "error": "Rate limit exceeded",
    "retry_after": 3600
}
```

---

## Authentication

### Getting JWT Token

```bash
curl -X POST http://localhost:5000/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Response:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 86400,
    "token_type": "Bearer"
}
```

### Using Token

```bash
curl -X GET http://localhost:5000/api/financial/cards/27123456789/balance \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

---

## Webhook Events

```
payment.transfer.completed
payment.transfer.failed
kyc.verified
kyc.rejected
card.balance.low (below R100)
biometric.enrollment_complete
bank_account.verified
```

---

## Support & Documentation

- **Main Docs**: See `PHASE_5_FINANCIAL_SYSTEM.md`
- **Integration Guide**: See `PHASE_5_INTEGRATION_GUIDE.md`
- **Verification**: See `PHASE_5_VERIFICATION.txt`

