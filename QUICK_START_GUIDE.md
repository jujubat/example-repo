# Tap Trip - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Firebase Account
- Payment Provider Accounts (Stripe, PayPal, Flutterwave)

### Installation

```bash
# 1. Navigate to project directory
cd Batuma_full_app

# 2. Create virtual environment (recommended)
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with your credentials
cp .env.example .env
# Edit .env with your actual API keys
```

### Environment Setup (.env)

```ini
# Firebase Configuration
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY=your_private_key

# Payment Providers
STRIPE_API_KEY=your_stripe_key
STRIPE_SECRET_KEY=your_stripe_secret

PAYPAL_CLIENT_ID=your_paypal_id
PAYPAL_SECRET=your_paypal_secret

FLUTTERWAVE_PUBLIC_KEY=your_flutterwave_key
FLUTTERWAVE_SECRET_KEY=your_flutterwave_secret

# SMS Provider
SMS_PROVIDER=twilio
SMS_API_KEY=your_twilio_key
SMS_ACCOUNT_SID=your_account_sid

# Google Maps
GOOGLE_MAPS_API_KEY=your_google_maps_key

# Email Service
EMAIL_SERVICE=sendgrid
EMAIL_API_KEY=your_sendgrid_key

# App Configuration
FLASK_ENV=production
DEBUG=False
```

### Running the App

#### Development Mode
```bash
python batuma_gprs_weather/app.py
```

App runs on `http://localhost:5000`

#### Production Mode (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 batuma_gprs_weather.app:app
```

---

## 🧪 Testing Core Features

### 1. Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "phone": "+27123456789",
    "password_hash": "hashed_password_here"
  }'
```

### 2. Calculate Ticket Price
```bash
curl -X POST http://localhost:5000/api/tickets/calculate-price \
  -H "Content-Type: application/json" \
  -d '{
    "start_station": "Main Station",
    "end_station": "Airport",
    "distance_km": 25,
    "ticket_type": "single"
  }'

# Response: Base R8.50 + (25 km × R1.50) = R46.00
```

### 3. Book a Ticket
```bash
curl -X POST http://localhost:5000/api/tickets/book \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123456",
    "route_id": "route_001",
    "start_station": "Main Station",
    "end_station": "Airport",
    "ticket_type": "daily",
    "price": 39.10
  }'

# Response: Ticket ID, QR code (Base64), 4 loyalty points earned
```

### 4. Create Virtual Card
```bash
curl -X POST http://localhost:5000/api/cards/create \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123456",
    "card_limit": 5000
  }'

# Response: Card number, CVV, expiry date, R5000 limit, R500 daily limit
```

### 5. Generate Share Code
```bash
curl -X POST http://localhost:5000/api/cards/share-code \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "card_id": "card_123456",
    "max_users": 5
  }'

# Response: 6-char alphanumeric code (e.g., "ABC123"), expires in 24 hours
```

### 6. Get Loyalty Balance
```bash
curl -X GET http://localhost:5000/api/loyalty/balance/user_123456 \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"

# Response: Current points, equivalent R value, next reward threshold
```

### 7. Find Nearby Restaurants
```bash
curl -X POST http://localhost:5000/api/restaurants/nearby \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": {"lat": -25.7479, "lon": 28.2293},
    "end_location": {"lat": -25.7589, "lon": 28.2293},
    "cuisine_preference": "Italian"
  }'

# Response: List of restaurants within delivery radius, distances, ratings
```

### 8. Place Restaurant Order
```bash
curl -X POST http://localhost:5000/api/restaurants/order/place \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123456",
    "restaurant_id": "rest_001",
    "items": [
      {"item_id": "item_001", "quantity": 1},
      {"item_id": "item_005", "quantity": 2}
    ],
    "delivery_address": {"lat": -25.7589, "lon": 28.2293},
    "special_instructions": "Extra cheese, no onions"
  }'

# Response: Order ID, total, estimated times, loyalty points earned
```

### 9. Process Payment
```bash
curl -X POST http://localhost:5000/api/payments/process \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.00,
    "currency": "ZAR",
    "provider": "stripe",
    "user_id": "user_123456",
    "description": "Bus ticket - Johannesburg to Cape Town"
  }'

# Response: Transaction ID, status, timestamp, receipt
```

### 10. Get Live ETA
```bash
curl -X POST http://localhost:5000/api/transit/eta/all-stops \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "route_id": "route_001",
    "current_location_index": 3
  }'

# Response: ETA for all stops from current location, traffic conditions, crowding levels
```

---

## 📊 Database Setup

### Firestore Collections to Create

```javascript
// Create these collections in Firebase Console:

1. users/
   - email (string)
   - phone (string)
   - failed_attempts (number)
   - locked_until (timestamp)

2. virtual_cards/
   - owner_id (string)
   - balance (number)
   - daily_limit_used (number)

3. tickets/
   - user_id (string)
   - status (string: active/used/expired/cancelled)

4. restaurants/
   - location (geolocation)
   - cuisine_type (string)

5. loyalty_points_balance/
   - balance (number)

6. live_tracking/
   - route_id (string)
   - vehicle_id (string)

7. restaurant_orders/
   - user_id (string)
   - status (string)

(Additional collections auto-created by code)
```

---

## 🔑 Key Features Quick Reference

| Feature | Endpoint | Key Fields |
|---------|----------|-----------|
| Register | POST /auth/register | email, phone, password |
| Login | POST /auth/login | email, password |
| Create Card | POST /cards/create | user_id, card_limit |
| Share Card | POST /cards/share-code | card_id, max_users |
| Book Ticket | POST /tickets/book | route_id, ticket_type, price |
| Calculate Price | POST /tickets/calculate-price | distance_km, ticket_type |
| Place Order | POST /restaurants/order/place | restaurant_id, items |
| Earn Points | POST /loyalty/earn | amount_spent, service_type |
| Redeem Points | POST /loyalty/redeem | service_type, quantity |
| Process Payment | POST /payments/process | amount, provider, currency |
| Get ETA | POST /transit/eta/all-stops | route_id, current_location |

---

## 💡 Example Workflows

### Workflow 1: Buy a Ticket
```
1. Register/Login
2. Calculate ticket price (POST /tickets/calculate-price)
3. Process payment (POST /payments/process)
4. Book ticket (POST /tickets/book)
5. Receive QR code + earn loyalty points
```

### Workflow 2: Share Virtual Card
```
1. Create virtual card (POST /cards/create)
2. Generate share code (POST /cards/share-code)
3. Share code with friends (via email/SMS/WhatsApp)
4. Friend adds card via code (POST /cards/add-user)
5. Friend can now use card (up to R500 daily limit)
6. Transactions >R500 need approval from card owner
```

### Workflow 3: Order Food
```
1. Find restaurants on route (POST /restaurants/nearby)
2. Browse menu (GET /restaurants/{id}/menu)
3. Place order (POST /restaurants/order/place)
4. Process payment (POST /payments/process)
5. Track order status (GET /restaurants/order/{id}/status)
6. Earn loyalty points (1 per R10)
7. Redeem points later
```

### Workflow 4: Real-Time Transit
```
1. Start live tracking (POST /transit/tracking/start)
2. Get ETA for all stops (POST /transit/eta/all-stops)
3. Update vehicle location (PUT /transit/tracking/{id}/location)
4. Receive real-time stop arrivals
5. Account for traffic delays
```

---

## 🐛 Common Issues & Solutions

### Issue: ModuleNotFoundError
**Solution:**
```bash
pip install -r requirements.txt
# Verify all modules: pip list
```

### Issue: Firebase Connection Error
**Solution:**
```bash
# Verify .env file has correct credentials
# Check Firebase project is active
# Confirm internet connection
```

### Issue: Payment Provider Error
**Solution:**
```bash
# Use test API keys for development
# Verify API keys in .env
# Check payment provider status page
```

### Issue: SMS Not Sending
**Solution:**
```bash
# Verify SMS provider (Twilio/AWS SNS) is configured
# Check API keys are correct
# Verify phone numbers in E.164 format (+27...)
```

### Issue: QR Code Not Generating
**Solution:**
```bash
# Verify qrcode and Pillow libraries installed
# Check file write permissions
# Verify base64 encoding is working
```

---

## 📈 Performance Tips

1. **Enable Database Indexing**
   - Create Firestore indexes for frequently queried fields
   - Example: user_id on transactions collection

2. **Implement Caching**
   ```python
   # Add Redis for session caching
   from redis import Redis
   cache = Redis(host='localhost', port=6379)
   ```

3. **Use Connection Pooling**
   - Firebase client already optimized
   - Firestore handles connection pooling

4. **Monitor Rate Limits**
   - 100 requests/minute per user (standard)
   - 10 requests/minute (payments)

---

## 🔒 Security Checklist

- [ ] All API keys in .env (never commit to git)
- [ ] HTTPS enabled on production
- [ ] CORS origins restricted to known domains
- [ ] Rate limiting enabled
- [ ] SQL injection prevention (using Firebase ODM)
- [ ] CSRF tokens for state-changing operations
- [ ] Password hashing implemented
- [ ] Session expiry set (24 hours)
- [ ] Audit logging enabled
- [ ] Security headers configured

---

## 📞 Support Resources

- **API Documentation:** See `TAP_TRIP_API_REFERENCE.md`
- **Implementation Details:** See `IMPLEMENTATION_SUMMARY.md`
- **Code Comments:** All functions have docstrings
- **Module Documentation:** See individual file headers

---

## 🚀 Next Steps

1. Configure all environment variables
2. Set up Firebase project and collections
3. Register with payment providers
4. Configure SMS provider
5. Run tests using provided curl examples
6. Deploy to production server
7. Monitor logs and transactions
8. Gather user feedback
9. Iterate on features

---

**Version:** 1.0  
**Last Updated:** January 20, 2024  
**Status:** Production Ready ✅

