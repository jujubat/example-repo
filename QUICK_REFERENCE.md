# Tap Trip Phase 2 - Quick Reference Guide

## 🚀 Quick Start

### Initialize the System

```python
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize Tap Trip Phase 2
from batuma_gprs_weather.routes.admin_routes import init_admin_routes
from batuma_gprs_weather.routes.customer_routes import init_customer_routes

init_admin_routes(db=db)
init_customer_routes(db=db)

# Register with Flask
app.register_blueprint(admin_routes)
app.register_blueprint(customer_routes)
```

---

## 📊 Admin Operations

### Login
```bash
curl -X POST http://localhost:5000/api/admin/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": "ADMIN001",
    "password_hash": "hash123"
  }'
```

### Create Station
```bash
curl -X POST http://localhost:5000/api/admin/stations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Central Bus Station",
    "location": {"latitude": -25.7461, "longitude": 28.2313},
    "type": "bus",
    "code": "CBS001"
  }'
```

### Get Top Clients
```bash
curl http://localhost:5000/api/admin/analytics/highest-paying?period=daily&limit=10 \
  -H "Authorization: Bearer {token}"
```

### Generate Report
```bash
curl http://localhost:5000/api/admin/reports/purchases?user_id=USR001&period=monthly \
  -H "Authorization: Bearer {token}"
```

### Export to CSV
```bash
curl -X POST http://localhost:5000/api/admin/reports/export \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "csv",
    "data": {"period": "monthly"}
  }'
```

---

## 💰 Customer Operations

### Load Points (from wallet)
```bash
curl -X POST http://localhost:5000/api/customer/loyalty/load-points/wallet \
  -H "Authorization: Bearer {token}" \
  -H "X-Customer-ID: CUST001" \
  -H "Content-Type: application/json" \
  -d '{
    "amount_rands": 100.00,
    "card_id": "CARD001"
  }'
```

### Request Point Transfer
```bash
curl -X POST http://localhost:5000/api/customer/loyalty/transfer-points \
  -H "Authorization: Bearer {token}" \
  -H "X-Customer-ID: CUST001" \
  -H "Content-Type: application/json" \
  -d '{
    "to_user_id": "CUST002",
    "points": 50,
    "message": "Here are some points!"
  }'
```

### Entry Scan
```bash
curl -X POST http://localhost:5000/api/customer/transit/scan-entry \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "qr_code": "STATION_001_1705320000",
    "card_id": "CARD001",
    "location": {
      "station_id": "STATION_001",
      "station_name": "Central Bus Station",
      "latitude": -25.7461,
      "longitude": 28.2313
    }
  }'
```

### Exit Scan
```bash
curl -X POST http://localhost:5000/api/customer/transit/scan-exit \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "scan_session_id": "SESSION_ABC123",
    "qr_code": "STATION_002_1705321200",
    "location": {
      "station_id": "STATION_002",
      "station_name": "Airport Station",
      "latitude": -25.6500,
      "longitude": 28.2400
    }
  }'
```

### Purchase Fuel
```bash
curl -X POST http://localhost:5000/api/customer/fuel/purchase \
  -H "Authorization: Bearer {token}" \
  -H "X-Customer-ID: CUST001" \
  -H "Content-Type: application/json" \
  -d '{
    "card_id": "CARD001",
    "station_id": "STATION_SHELL_001",
    "pump_id": "PUMP_15",
    "amount_rands": 200.00,
    "litres": 25.0
  }'
```

---

## 🔑 Key Constants

```python
# Points Formula
POINTS_PER_100_RANDS = 10
RANDS_PER_POINT = 0.5

# Balance Threshold
LOW_BALANCE_THRESHOLD_RANDS = 20.0
LOW_BALANCE_THRESHOLD_POINTS = 40

# Pricing
DEFAULT_FARE = 8.50
PEAK_MULTIPLIER = 1.2
OFF_PEAK_MULTIPLIER = 0.8
WEEKEND_MULTIPLIER = 0.9

# Times
PEAK_HOURS_START = "06:00"
PEAK_HOURS_END = "09:00"
```

---

## 📂 Directory Structure

```
batuma_gprs_weather/
├── admin/
│   ├── admin_dashboard.py      # Admin control hub
│   ├── reporting_system.py     # Financial reports
│   └── analytics.py            # Business analytics
├── payments/
│   ├── point_loading.py        # Point loading & transfer
│   └── fuel_purchase.py        # Fuel transactions
├── transit/
│   └── qr_scanning.py          # QR entry/exit
└── routes/
    ├── admin_routes.py         # Admin API endpoints
    └── customer_routes.py      # Customer API endpoints
```

---

## 🗄️ Firestore Collections

| Collection | Purpose | Key Fields |
|-----------|---------|-----------|
| `users` | Customer data | email, phone, wallet_balance |
| `virtual_cards` | Customer cards | owner_id, loyalty_points, is_default |
| `stations` | Transit stations | name, location, code, is_active |
| `petrol_stations` | Fuel stations | name, provider, set_rate |
| `tickets` | Transit trips | card_id, price, points_deducted |
| `scan_sessions` | QR sessions | entry_scan, exit_scan, status |
| `fuel_purchases` | Fuel transactions | amount, points_earned, station_id |
| `dynamic_pricing` | Pricing rules | route_id, rules {} |
| `point_transfer_requests` | Transfer workflow | from_user, to_user, status |
| `admin_users` | Admin accounts | email, role, permissions |

---

## 🔐 Authentication

### Admin Headers
```
Authorization: Bearer {jwt_token}
X-Admin-ID: ADMIN001
```

### Customer Headers
```
Authorization: Bearer {jwt_token}
X-Customer-ID: CUST001
```

---

## 📈 Report Periods

| Period | Range | Example Query |
|--------|-------|---------|
| **hourly** | Single hour | `?period=hourly&date=2024-01-15` |
| **daily** | 24 hours | `?period=daily&date=2024-01-15` |
| **weekly** | Mon-Sun | `?period=weekly&date=2024-01-15` |
| **monthly** | 1st-end | `?period=monthly&date=2024-01-15` |
| **yearly** | Jan 1-Dec 31 | `?period=yearly&date=2024-01-15` |
| **overall** | All time | `?period=overall` |

---

## 💡 Common Patterns

### Check if Customer Can Load Points
```python
from batuma_gprs_weather.payments.point_loading import PointLoadingSystem

point_loading = PointLoadingSystem(db=db)
result = point_loading.check_load_points_eligibility(user_id)

if result['eligible']:
    print(f"Wallet balance: R{result['wallet_balance']}")
```

### Process Point Transfer
```python
from batuma_gprs_weather.payments.point_loading import PointTransferSystem

transfer = PointTransferSystem(db=db)

# Request
result = transfer.request_point_transfer(
    from_user_id="CUST001",
    to_user_id="CUST002",
    points=50
)

# Get pending
requests = transfer.get_pending_transfer_requests("CUST002")

# Approve
result = transfer.approve_transfer_request(req_id, "CUST002")
```

### Generate Monthly Report
```python
from batuma_gprs_weather.admin.reporting_system import ReportingSystem

reports = ReportingSystem(db=db)
result = reports.get_purchase_report(
    user_id="CUST001",
    period="monthly",
    date=datetime.now()
)

print(f"Total spent: R{result['total_spent']}")
print(f"Points earned: {result['points_earned']}")
```

### Get Top Clients
```python
from batuma_gprs_weather.admin.analytics import AnalyticsEngine

analytics = AnalyticsEngine(db=db)
result = analytics.get_highest_paying_clients(period="daily", limit=10)

for client in result['top_clients']:
    print(f"{client['email']}: R{client['total_spent']}")
```

---

## 🎯 Points Calculation

### Loading Points
```
Amount (R) → Points
100.00    → 10
250.00    → 25
500.00    → 50
1000.00   → 100
```

### Spending Points
```
Fare (R) → Points Deducted
8.50     → 1 (rounded up)
15.50    → 2 (rounded up)
50.00    → 5
100.00   → 10
```

### Point Transfer
```
Points to Transfer → Value (R)
10                → 5.00
50                → 25.00
100               → 50.00
```

---

## 🚨 Error Handling

### Standard Error Response
```json
{
  "success": false,
  "error": "Insufficient points",
  "code": 400
}
```

### Common Errors

| Error | Status | Solution |
|-------|--------|----------|
| Invalid authorization | 401 | Check token and headers |
| Insufficient balance | 400 | Load more points |
| User not found | 404 | Verify user_id |
| Station not found | 404 | Create station first |
| Transfer expired | 400 | Create new request |

---

## 📊 Database Queries

### Get User's Recent Trips
```python
trips = db.collection('tickets')\
    .where('user_id', '==', 'CUST001')\
    .order_by('issue_date', direction='DESCENDING')\
    .limit(10)\
    .stream()
```

### Get Monthly Revenue
```python
from datetime import datetime, timedelta

start = datetime(2024, 1, 1)
end = datetime(2024, 1, 31, 23, 59, 59)

transactions = db.collection('tickets')\
    .where('issue_date', '>=', start)\
    .where('issue_date', '<=', end)\
    .stream()

total = sum(t.to_dict()['price'] for t in transactions)
```

### Get Top Stations
```python
stations = db.collection('stations')\
    .where('is_active', '==', True)\
    .order_by('transaction_count', direction='DESCENDING')\
    .limit(5)\
    .stream()
```

---

## 🔧 Troubleshooting

### Points Not Loading
1. Check wallet balance
2. Verify card is active
3. Check points formula: (amount/100)*10
4. Review Firestore permissions

### Transfer Request Expired
1. Check expiry_date in database
2. Create new transfer request
3. Verify recipient is active

### Low Balance Alert Not Showing
1. Confirm threshold: R20 = 40 points
2. Check balance calculation
3. Verify alert logic triggered

### Report Export Timeout
1. Reduce date range
2. Filter by single user
3. Increase server timeout
4. Use smaller batch size

---

## 📚 Documentation Links

- **Full Documentation**: `PHASE_2_DOCUMENTATION.md`
- **Implementation Details**: `PHASE_2_IMPLEMENTATION_SUMMARY.md`
- **API Reference**: `PHASE_2_DOCUMENTATION.md#api-reference`
- **Database Schema**: `PHASE_2_DOCUMENTATION.md#database-schema`

---

## 🎓 Examples

### Complete Admin Workflow
```python
# 1. Login
admin_dash = AdminDashboard(db=db)
admin = admin_dash.authenticate_admin("ADMIN001", "hash123")

# 2. Create station
station = admin_dash.add_station(
    name="Airport Station",
    location={"latitude": -25.64, "longitude": 28.24},
    station_type="bus",
    code="AS001"
)

# 3. Set pricing
pricing = admin_dash.set_dynamic_pricing(
    route_id="ROUTE_001",
    rules={"base_price": 10.50}
)

# 4. Get reports
reports = ReportingSystem(db=db)
daily_report = reports.get_all_customers_report("daily")
print(f"Daily revenue: R{daily_report['grand_total_spent']}")
```

### Complete Customer Workflow
```python
from batuma_gprs_weather.payments.point_loading import PointLoadingSystem
from batuma_gprs_weather.transit.qr_scanning import QRScanSystem

# 1. Load points
point_loading = PointLoadingSystem(db=db)
result = point_loading.load_points_from_wallet("CUST001", 100.00)
print(f"Points loaded: {result['points_loaded']}")

# 2. Scan entry
qr_scanner = QRScanSystem(db=db)
entry = qr_scanner.scan_entry(
    qr_code="STATION_001",
    card_id="CARD001",
    location={"station_id": "STATION_001", "station_name": "Central"}
)
session_id = entry['scan_session_id']

# 3. Scan exit
exit_result = qr_scanner.scan_exit(
    scan_session_id=session_id,
    qr_code="STATION_002",
    location={"station_id": "STATION_002", "station_name": "Airport"}
)
print(f"Fare: R{exit_result['fare_amount']}")
print(f"Points used: {exit_result['points_deducted']}")
```

---

## 📞 Support

For questions or issues, refer to:
1. `PHASE_2_DOCUMENTATION.md` for detailed information
2. API error messages for specific issues
3. Firestore console for data verification
4. Server logs for debug information

---

## Version Info
- **Release**: 2024-01-15
- **Version**: 2.0.0
- **Status**: Production Ready
