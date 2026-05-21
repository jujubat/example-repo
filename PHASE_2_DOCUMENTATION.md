# Tap Trip Phase 2 - Admin Back Office & Enhanced Features
## Complete Implementation Guide

---

## Table of Contents
1. [Overview](#overview)
2. [Admin Back Office](#admin-back-office)
3. [Analytics & Reporting](#analytics--reporting)
4. [Customer Features](#customer-features)
5. [API Reference](#api-reference)
6. [Database Schema](#database-schema)
7. [Configuration](#configuration)

---

## Overview

Phase 2 extends the Tap Trip platform with comprehensive admin controls, advanced analytics, and enhanced customer loyalty features. The system now includes:

- **Admin Dashboard**: Role-based management of stations, pricing, and users
- **Advanced Reporting**: Multi-period reports with CSV/PDF export
- **Analytics Engine**: Geographic and behavioral analytics
- **Point Management**: Loading, transfer, and earning system
- **QR Transit System**: Entry/exit scanning with fare calculation
- **Fuel Integration**: Virtual card purchases at petrol stations

### Key Statistics

- **Lines of Code**: 3,500+ new lines of production-ready code
- **New Modules**: 6 major systems
- **API Endpoints**: 40+ REST endpoints
- **Database Collections**: 15+ Firestore collections
- **Points Formula**: R100 = 10 points = R0.5 each

---

## Admin Back Office

### Features

The admin dashboard provides comprehensive control for transportation operators:

#### 1. **Station Management**
- Create and deactivate transit stations
- Track station performance
- Manage station codes

**Endpoint**: `POST /api/admin/stations`

```json
{
  "name": "Central Bus Station",
  "location": {
    "latitude": -25.7461,
    "longitude": 28.2313,
    "address": "123 Main St"
  },
  "type": "bus",
  "code": "CBS001"
}
```

#### 2. **Dynamic Pricing**
Configure pricing based on multiple factors:
- Time of day (peak/off-peak)
- Day of week (weekday/weekend)
- Route-specific multipliers

**Endpoint**: `POST /api/admin/pricing`

```json
{
  "route_id": "route_001",
  "rules": {
    "base_price": 8.50,
    "time_based": {
      "peak_hours": {
        "start": "06:00",
        "end": "09:00",
        "multiplier": 1.2
      },
      "off_peak": {
        "multiplier": 0.8
      }
    },
    "day_based": {
      "weekday_multiplier": 1.0,
      "weekend_multiplier": 0.9
    }
  }
}
```

#### 3. **Account Management**
- Deactivate/activate user accounts
- View user details and history
- Monitor account balance

**Endpoints**:
- `PUT /api/admin/users/{user_id}/deactivate`
- `PUT /api/admin/users/{user_id}/activate`
- `GET /api/admin/users/{user_id}`

#### 4. **Petrol Station Management**
Add fuel stations where customers can purchase with virtual cards.

**Endpoint**: `POST /api/admin/petrol-stations`

```json
{
  "name": "Shell Sandton",
  "location": {
    "latitude": -25.7461,
    "longitude": 28.2313
  },
  "provider": "Shell",
  "set_rate": 1.2
}
```

### Admin Role System

Three-tier permission structure:

| Role | Permissions |
|------|------------|
| **SUPER_ADMIN** | All operations, user management, role assignment |
| **ADMIN** | Station/pricing management, user account control |
| **MANAGER** | View-only access to reports and analytics |

---

## Analytics & Reporting

### Reporting System

Comprehensive financial reports with multiple time periods:

**Supported Periods**:
- Hourly (per hour breakdown)
- Daily (24-hour period)
- Weekly (Monday-Sunday)
- Monthly (1st to end of month)
- Yearly (Jan 1 - Dec 31)
- Overall (all data)

#### Getting Reports

**Single User Report**:
```
GET /api/admin/reports/purchases?user_id=USER123&period=daily&date=2024-01-15
```

Response:
```json
{
  "success": true,
  "user_id": "USER123",
  "period": "daily",
  "total_spent": 245.50,
  "points_earned": 246,
  "transaction_count": 12,
  "average_transaction": 20.45
}
```

**All Customers Report**:
```
GET /api/admin/reports/all-customers?period=monthly&folder=all
```

Response:
```json
{
  "success": true,
  "period": "monthly",
  "grand_total_spent": 12500.00,
  "grand_total_points": 12500,
  "total_transactions": 1500
}
```

### Analytics Engine

#### Highest Paying Clients

Get top-spending customers by period.

**Endpoint**: `GET /api/admin/analytics/highest-paying?period=day&limit=10`

Response:
```json
{
  "success": true,
  "period": "daily",
  "top_clients": [
    {
      "user_id": "USR001",
      "email": "john@example.com",
      "total_spent": 450.25,
      "transaction_count": 25,
      "average_per_transaction": 18.01,
      "points_earned": 450
    }
  ]
}
```

#### Geographic Breakdown

Spending by location (station/area).

**Endpoint**: `GET /api/admin/analytics/geographic?period=weekly`

Response:
```json
{
  "success": true,
  "by_station": [
    {
      "name": "Central Station",
      "location": {"lat": -25.7461, "lng": 28.2313},
      "total_spent": 2500.00,
      "transaction_count": 250
    }
  ]
}
```

#### Top Used Cards

Most frequently used virtual cards.

**Endpoint**: `GET /api/admin/analytics/top-cards?limit=10`

Response:
```json
{
  "success": true,
  "most_used_cards": [
    {
      "card_id": "CARD001",
      "usage_count": 150,
      "owner": {
        "user_id": "USR001",
        "email": "john@example.com"
      }
    }
  ]
}
```

#### Graph Data

Pre-formatted data for various chart types.

**Area Chart**:
```
GET /api/admin/analytics/chart/area?metric=revenue&period=daily
```

**Bar Chart**:
```
GET /api/admin/analytics/chart/bar?metric=top_clients&period=weekly
```

**Pie Chart**:
```
GET /api/admin/analytics/chart/pie?metric=by_station&period=monthly
```

### Export Features

#### CSV Export

```
POST /api/admin/reports/export
Content-Type: application/json

{
  "format": "csv",
  "data": {
    "period": "monthly",
    "include_user_details": true
  }
}
```

Response:
```csv
Date,User Email,Total Spent,Points Earned,Transactions
2024-01-01,john@example.com,245.50,246,12
2024-01-02,jane@example.com,180.25,180,8
```

#### PDF Export

```
POST /api/admin/reports/export
Content-Type: application/json

{
  "format": "pdf",
  "data": {
    "period": "monthly",
    "title": "Monthly Financial Report"
  }
}
```

---

## Customer Features

### Point Loading System

Customers can load points using multiple methods:

#### From Wallet Balance

```
POST /api/customer/loyalty/load-points/wallet
Content-Type: application/json
Authorization: Bearer {token}
X-Customer-ID: {customer_id}

{
  "amount_rands": 100.00,
  "card_id": "CARD001"
}
```

Response:
```json
{
  "success": true,
  "points_loaded": 10,
  "amount_deducted": 100.00,
  "new_card_balance": 150,
  "points_value_rands": 5.00,
  "new_wallet_balance": 400.00
}
```

**Note**: R100 = 10 points = R5.00 in value

#### Bank Transfer

```
POST /api/customer/loyalty/load-points/bank-transfer
Content-Type: application/json
Authorization: Bearer {token}
X-Customer-ID: {customer_id}

{
  "amount_rands": 500.00,
  "card_id": "CARD001"
}
```

Generates bank reference for transfer confirmation.

#### Promo Codes

```
POST /api/customer/loyalty/load-points/promo
Content-Type: application/json
Authorization: Bearer {token}
X-Customer-ID: {customer_id}

{
  "promo_code": "SUMMER2024",
  "card_id": "CARD001"
}
```

### Point Transfer System

Transfer points to other users with approval workflow.

#### Request Transfer

```
POST /api/customer/loyalty/transfer-points
Content-Type: application/json
Authorization: Bearer {token}
X-Customer-ID: {from_user_id}

{
  "to_user_id": "USR002",
  "points": 50,
  "message": "Here are some points for you!"
}
```

#### View Pending Requests

```
GET /api/customer/loyalty/transfer-requests
Authorization: Bearer {token}
X-Customer-ID: {customer_id}
```

Response:
```json
{
  "success": true,
  "pending_requests": [
    {
      "request_id": "REQ001",
      "from_user": {
        "user_id": "USR001",
        "email": "john@example.com"
      },
      "points": 50,
      "rands_equivalent": 25.00,
      "message": "Here are some points",
      "created_at": "2024-01-15T10:30:00Z",
      "expires_at": "2024-01-22T10:30:00Z"
    }
  ]
}
```

#### Approve Transfer

```
PUT /api/customer/loyalty/transfer-requests/{request_id}/approve
Authorization: Bearer {token}
X-Customer-ID: {customer_id}
```

Points are automatically transferred upon approval.

### QR Scanning System

Entry/exit scanning for transit journeys with automatic fare calculation.

#### Entry Scan

```
POST /api/customer/transit/scan-entry
Content-Type: application/json
Authorization: Bearer {token}

{
  "qr_code": "STATION_001_1705320000",
  "card_id": "CARD001",
  "location": {
    "station_id": "STATION_001",
    "station_name": "Central Bus Station",
    "latitude": -25.7461,
    "longitude": 28.2313
  }
}
```

Response:
```json
{
  "success": true,
  "scan_session_id": "SESSION_ABC123",
  "entry_recorded": true,
  "station": "Central Bus Station",
  "current_balance": 75.50,
  "current_points": 151
}
```

#### Exit Scan

```
POST /api/customer/transit/scan-exit
Content-Type: application/json
Authorization: Bearer {token}

{
  "scan_session_id": "SESSION_ABC123",
  "qr_code": "STATION_002_1705321200",
  "location": {
    "station_id": "STATION_002",
    "station_name": "Airport Bus Station",
    "latitude": -25.6500,
    "longitude": 28.2400
  }
}
```

Response:
```json
{
  "success": true,
  "ticket_id": "TICKET_001",
  "journey_complete": true,
  "from_station": "Central Bus Station",
  "to_station": "Airport Bus Station",
  "fare_amount": 15.50,
  "points_deducted": 16,
  "previous_balance": 151,
  "new_balance": 135,
  "new_balance_rands": 67.50,
  "journey_time_minutes": 35,
  "low_balance_alert": {
    "triggered": false,
    "current_balance": 67.50
  }
}
```

#### Low Balance Alert

If balance drops below R20 (40 points):

```json
{
  "low_balance_alert": {
    "triggered": true,
    "current_balance": 15.00,
    "current_points": 30,
    "threshold": 20.00,
    "message": "Your points or balance is low. Current: 30 points (R15.00). Minimum required: R20.00 (40 points)"
  }
}
```

### Fuel Purchase System

Purchase fuel at integrated petrol stations.

#### Purchase Fuel

```
POST /api/customer/fuel/purchase
Content-Type: application/json
Authorization: Bearer {token}
X-Customer-ID: {customer_id}

{
  "card_id": "CARD001",
  "station_id": "STATION_SHELL_001",
  "pump_id": "PUMP_15",
  "amount_rands": 200.00,
  "litres": 25.0
}
```

Response:
```json
{
  "success": true,
  "transaction_id": "FUEL_TX_001",
  "receipt_number": "FP20240115141530",
  "station": "Shell Sandton",
  "pump_id": "PUMP_15",
  "amount_charged": 200.00,
  "litres_dispensed": 25.0,
  "points_used": 20,
  "points_earned": 24,
  "new_balance": 155,
  "new_balance_rands": 77.50,
  "message": "Fuel purchased successfully! You earned 24 bonus points."
}
```

#### Fuel Receipt

```
GET /api/customer/fuel/receipt/{transaction_id}
Authorization: Bearer {token}
```

Response:
```json
{
  "success": true,
  "receipt": {
    "receipt_number": "FP20240115141530",
    "date": "2024-01-15",
    "time": "14:15:30",
    "station": "Shell Sandton",
    "provider": "Shell",
    "pump_id": "PUMP_15",
    "amount": "R200.00",
    "litres": "25.00L",
    "unit_price": "R8.00/L",
    "points_earned": 24,
    "points_value": "R12.00"
  }
}
```

---

## API Reference

### Authentication

All endpoints require authentication headers:

```
Authorization: Bearer {token}
X-Customer-ID: {customer_id}  # For customer endpoints
X-Admin-ID: {admin_id}        # For admin endpoints
```

### Response Format

All responses follow standard format:

```json
{
  "success": true/false,
  "message": "Human-readable message",
  "data": { /* endpoint-specific data */ },
  "error": "Error message if success=false"
}
```

### Error Codes

| Code | Status | Meaning |
|------|--------|---------|
| 200 | OK | Success |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing/invalid auth |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal error |

### Rate Limiting

- Admin endpoints: 1000 requests/hour
- Customer endpoints: 500 requests/hour
- Reporting endpoints: 100 requests/hour

---

## Database Schema

### Collections Structure

```
firestore/
├── users/
│   ├── email
│   ├── phone
│   ├── is_active
│   ├── wallet_balance
│   ├── created_at
│   └── ...
├── virtual_cards/
│   ├── owner_id
│   ├── card_number
│   ├── loyalty_points
│   ├── is_default
│   ├── is_active
│   └── ...
├── stations/
│   ├── name
│   ├── location (lat/lng)
│   ├── type (bus/train/etc)
│   ├── code
│   └── is_active
├── petrol_stations/
│   ├── name
│   ├── location
│   ├── provider
│   ├── set_rate
│   └── ...
├── tickets/
│   ├── card_id
│   ├── user_id
│   ├── start_station
│   ├── end_station
│   ├── price
│   ├── points_deducted
│   ├── issue_date
│   └── ...
├── scan_sessions/
│   ├── card_id
│   ├── entry_scan
│   ├── exit_scan
│   ├── status
│   └── ...
├── fuel_purchases/
│   ├── card_id
│   ├── user_id
│   ├── station_id
│   ├── amount
│   ├── points_earned
│   ├── purchase_date
│   └── ...
├── dynamic_pricing/
│   ├── route_id
│   ├── rules {}
│   └── ...
├── point_loading_transactions/
│   ├── user_id
│   ├── points_loaded
│   ├── amount_rands
│   ├── method
│   └── ...
├── point_transfer_requests/
│   ├── from_user_id
│   ├── to_user_id
│   ├── points
│   ├── status
│   └── ...
├── admin_users/
│   ├── email
│   ├── role
│   ├── permissions []
│   └── ...
└── loyalty_points_balance/
    ├── user_id
    ├── total_earned
    ├── total_redeemed
    ├── current_balance
    └── ...
```

---

## Configuration

### Environment Variables

```env
# Firebase
FIREBASE_API_KEY=your_api_key
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_AUTH_DOMAIN=your_auth_domain

# Points Configuration
POINTS_PER_100_RANDS=10
RANDS_PER_POINT=0.5
LOW_BALANCE_THRESHOLD_RANDS=20.0

# Admin Settings
ADMIN_JWT_SECRET=your_secret_key
ADMIN_SESSION_TIMEOUT=3600

# Pricing
DEFAULT_FARE=8.50
PEAK_MULTIPLIER=1.2
OFF_PEAK_MULTIPLIER=0.8
WEEKEND_MULTIPLIER=0.9

# Reports
EXPORT_TIMEOUT=300
MAX_EXPORT_ROWS=100000
```

### Initialize Systems

```python
from batuma_gprs_weather.admin.admin_dashboard import AdminDashboard
from batuma_gprs_weather.admin.reporting_system import ReportingSystem
from batuma_gprs_weather.admin.analytics import AnalyticsEngine
from batuma_gprs_weather.payments.point_loading import PointLoadingSystem, PointTransferSystem
from batuma_gprs_weather.transit.qr_scanning import QRScanSystem
from batuma_gprs_weather.payments.fuel_purchase import FuelPurchaseSystem

# Initialize
db = firebase.firestore.client()

admin_dashboard = AdminDashboard(db=db)
reporting_system = ReportingSystem(db=db)
analytics_engine = AnalyticsEngine(db=db)
point_loading = PointLoadingSystem(db=db)
point_transfer = PointTransferSystem(db=db)
qr_scanner = QRScanSystem(db=db)
fuel_system = FuelPurchaseSystem(db=db)

# Register Flask blueprints
from batuma_gprs_weather.routes.admin_routes import admin_routes, init_admin_routes
from batuma_gprs_weather.routes.customer_routes import customer_routes, init_customer_routes

app.register_blueprint(admin_routes)
app.register_blueprint(customer_routes)

init_admin_routes(db=db)
init_customer_routes(db=db)
```

---

## Points System

### Formula

- **Loading**: R100 = 10 points
- **Earning**: 1 point per R10 spent
- **Value**: 1 point = R0.50
- **Transfer**: Full 1:1 ratio

### Examples

**Loading Points**:
- R100 wallet → 10 points → R5.00 value
- R500 bank transfer → 50 points → R25.00 value
- R250 fuel → 25 points earned (if set_rate=1.0)

**Using Points**:
- R15.50 fare → 16 points deducted (rounded up)
- 40 points minimum = R20.00 (low balance threshold)

---

## Performance Notes

- Reports can handle up to 100,000 transactions
- Export operations timeout after 5 minutes
- Analytics queries are cached for 1 hour
- Bulk operations recommended for >1000 records

---

## Support & Troubleshooting

### Common Issues

**Low Balance Alert Not Showing**:
- Verify threshold is set to R20.00
- Check points calculation: (balance_rands / 0.50) = points

**Points Transfer Failing**:
- Verify recipient has active account
- Confirm sender has sufficient points
- Check approval workflow status

**Report Export Timeout**:
- Reduce date range
- Filter by specific user or period
- Check database query performance

---

## Version Information

- **Phase 2 Release**: 2024-01-15
- **Version**: 2.0.0
- **Database**: Firestore Real-time
- **API Framework**: Flask 2.3.2
- **Python**: 3.8+

