# Tap Trip API Reference
**Multi-Modal Transportation, Payments & Loyalty Platform**

---

## Table of Contents
1. [Authentication](#authentication)
2. [Payment Gateway](#payment-gateway)
3. [Virtual Cards](#virtual-cards)
4. [Tickets](#tickets)
5. [Restaurants](#restaurants)
6. [Loyalty Points](#loyalty-points)
7. [Transit & Real-Time ETA](#transit--real-time-eta)
8. [Error Handling](#error-handling)

---

## Authentication

All endpoints (except public routes) require Bearer token authentication:

```
Authorization: Bearer {session_token}
```

### Register User
```
POST /api/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "phone": "+27123456789",
    "password_hash": "hashed_password"
}

Response:
{
    "success": true,
    "user_id": "user_123456",
    "message": "Account created. Verification code sent."
}
```

### Login
```
POST /api/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password_hash": "hashed_password"
}

Response:
{
    "success": true,
    "user_id": "user_123456",
    "session_token": "token_123456",
    "expires_in": 86400
}
```

### Verify Email
```
POST /api/auth/verify-email

{
    "user_id": "user_123456",
    "verification_code": "123456"
}

Response:
{
    "success": true,
    "message": "Email verified successfully"
}
```

---

## Payment Gateway

### Process Payment
```
POST /api/payments/process
Authorization: Bearer {token}

{
    "amount": 500.00,
    "currency": "ZAR",
    "provider": "stripe|paypal|flutterwave",
    "user_id": "user_123456",
    "description": "Bus ticket - JNB to CPT"
}

Response:
{
    "success": true,
    "transaction_id": "txn_123456",
    "amount": 500.00,
    "currency": "ZAR",
    "status": "completed",
    "timestamp": "2024-01-20T10:30:00"
}
```

### Verify Payment
```
GET /api/payments/verify/{transaction_id}
Authorization: Bearer {token}

Response:
{
    "success": true,
    "transaction_id": "txn_123456",
    "status": "verified",
    "amount": 500.00
}
```

### Refund Payment
```
POST /api/payments/refund/{transaction_id}
Authorization: Bearer {token}

{
    "amount": 500.00,
    "reason": "Customer cancellation"
}

Response:
{
    "success": true,
    "refund_amount": 500.00,
    "status": "refund_processed",
    "refund_id": "ref_123456"
}
```

### Payment History
```
GET /api/payments/history/{user_id}?limit=20&offset=0
Authorization: Bearer {token}

Response:
{
    "success": true,
    "user_id": "user_123456",
    "transactions": [
        {
            "transaction_id": "txn_001",
            "amount": 500.00,
            "date": "2024-01-15T10:30:00",
            "description": "Bus ticket",
            "status": "completed"
        }
    ],
    "total": 25
}
```

---

## Virtual Cards

### Create Virtual Card
```
POST /api/cards/create
Authorization: Bearer {token}

{
    "user_id": "user_123456",
    "card_limit": 5000
}

Response:
{
    "success": true,
    "card_id": "card_123456",
    "card_number": "4532 **** **** 1234",
    "expiry": "12/27",
    "cvv": "***",
    "limit": 5000,
    "daily_limit": 500,
    "status": "active"
}
```

### Generate Share Code
```
POST /api/cards/share-code
Authorization: Bearer {token}

{
    "card_id": "card_123456",
    "max_users": 5
}

Response:
{
    "success": true,
    "card_id": "card_123456",
    "share_code": "ABC123XYZ",
    "expires_at": "2024-01-21T10:30:00",
    "max_users": 5,
    "message": "Share code generated. Valid for 24 hours."
}
```

### Add Shared User
```
POST /api/cards/add-user
Authorization: Bearer {token}

{
    "share_code": "ABC123XYZ",
    "user_id": "user_654321"
}

Response:
{
    "success": true,
    "card_id": "card_123456",
    "user_added": "user_654321",
    "status": "user_added",
    "message": "Card successfully added to your account"
}
```

### Request Transaction Approval
```
POST /api/cards/request-approval
Authorization: Bearer {token}

{
    "card_id": "card_123456",
    "amount": 750.00,
    "description": "Restaurant order",
    "requester_id": "user_654321"
}

Response:
{
    "success": true,
    "approval_id": "appr_123456",
    "amount": 750.00,
    "status": "approval_requested",
    "expires_at": "2024-01-20T11:30:00",
    "message": "Approval request sent to card owner"
}
```

### Approve/Decline Transaction
```
PUT /api/cards/approve/{approval_id}
Authorization: Bearer {token}

{
    "approved": true
}

Response:
{
    "success": true,
    "approval_id": "appr_123456",
    "status": "approved",
    "message": "Transaction approved"
}
```

### Get Card Transactions
```
GET /api/cards/{card_id}/transactions?limit=50
Authorization: Bearer {token}

Response:
{
    "success": true,
    "card_id": "card_123456",
    "transactions": [
        {
            "transaction_id": "txn_001",
            "amount": 150.00,
            "date": "2024-01-20T10:30:00",
            "description": "Food order",
            "location": "Restaurant XYZ",
            "status": "completed"
        }
    ],
    "total": 15
}
```

---

## Tickets

### Calculate Ticket Price
```
POST /api/tickets/calculate-price

{
    "start_station": "Main Station",
    "end_station": "Airport",
    "distance_km": 25,
    "ticket_type": "single"
}

Response:
{
    "success": true,
    "start_station": "Main Station",
    "end_station": "Airport",
    "distance_km": 25,
    "ticket_type": "single",
    "base_price": 48.50,
    "final_price": 48.50,
    "discount_percent": 0,
    "points_earned": 4
}
```

**Pricing Formula:**
- Base: R8.50
- Rate: R1.50 per km
- Discounts: Daily (15%), Weekly (30%), Monthly (45%)
- Points: 1 point per R10

### Book Ticket
```
POST /api/tickets/book
Authorization: Bearer {token}

{
    "user_id": "user_123456",
    "route_id": "route_001",
    "start_station": "Main Station",
    "end_station": "Airport",
    "ticket_type": "daily",
    "price": 41.23
}

Response:
{
    "success": true,
    "ticket_id": "ticket_123456",
    "status": "active",
    "qr_code": "data:image/png;base64,...",
    "receipt_id": "receipt_123456",
    "points_earned": 4,
    "valid_until": "2024-01-21T10:30:00"
}
```

### Validate Ticket
```
GET /api/tickets/validate/{ticket_id}

Response:
{
    "success": true,
    "ticket_id": "ticket_123456",
    "status": "valid",
    "valid_until": "2024-01-21T10:30:00"
}
```

### Get User Tickets
```
GET /api/tickets/user/{user_id}?status=active
Authorization: Bearer {token}

Response:
{
    "success": true,
    "user_id": "user_123456",
    "tickets": [
        {
            "ticket_id": "ticket_001",
            "type": "daily",
            "start_station": "Main Station",
            "end_station": "Airport",
            "status": "active",
            "valid_until": "2024-01-21T10:30:00"
        }
    ],
    "total": 5
}
```

---

## Restaurants

### Find Nearby Restaurants
```
POST /api/restaurants/nearby
Authorization: Bearer {token}

{
    "start_location": {"lat": -25.7479, "lon": 28.2293},
    "end_location": {"lat": -25.7589, "lon": 28.2293},
    "cuisine_preference": "Italian"
}

Response:
{
    "success": true,
    "restaurants": [
        {
            "restaurant_id": "rest_001",
            "name": "Restaurant Name",
            "location": {"lat": -25.7489, "lon": 28.2293},
            "cuisine_type": "Italian",
            "rating": 4.5,
            "distance_km": 1.2,
            "prep_time_estimated": "20-30 mins",
            "delivery_fee": 15.00,
            "min_order": 50.00
        }
    ],
    "total": 8
}
```

### Get Restaurant Menu
```
GET /api/restaurants/{restaurant_id}/menu

Response:
{
    "success": true,
    "restaurant_id": "rest_001",
    "menu_items": [
        {
            "item_id": "item_001",
            "name": "Margherita Pizza",
            "description": "Classic pizza with tomato and mozzarella",
            "price": 120.00,
            "category": "Pizzas",
            "prep_time": "15-20 mins",
            "available": true,
            "rating": 4.8
        }
    ],
    "total_items": 45
}
```

### Place Order
```
POST /api/restaurants/order/place
Authorization: Bearer {token}

{
    "user_id": "user_123456",
    "restaurant_id": "rest_001",
    "items": [
        {"item_id": "item_001", "quantity": 1},
        {"item_id": "item_005", "quantity": 2}
    ],
    "delivery_address": {"lat": -25.7589, "lon": 28.2293},
    "special_instructions": "Extra cheese, no onions"
}

Response:
{
    "success": true,
    "order_id": "order_123456",
    "restaurant_name": "Restaurant Name",
    "total_amount": 350.00,
    "delivery_fee": 15.00,
    "grand_total": 365.00,
    "estimated_ready_time": "2024-01-20T10:55:00",
    "estimated_delivery_time": "2024-01-20T11:10:00",
    "points_earned": 36,
    "message": "Order confirmed"
}
```

### Get Order Status
```
GET /api/restaurants/order/{order_id}/status
Authorization: Bearer {token}

Response:
{
    "success": true,
    "order_id": "order_123456",
    "status": "preparing",
    "estimated_ready_time": "2024-01-20T10:55:00",
    "estimated_delivery_time": "2024-01-20T11:10:00"
}
```

---

## Loyalty Points

### Earn Points
```
POST /api/loyalty/earn
Authorization: Bearer {token}

{
    "user_id": "user_123456",
    "amount_spent": 150.00,
    "service_type": "ticket",
    "description": "Bus ticket purchased"
}

Response:
{
    "success": true,
    "user_id": "user_123456",
    "points_earned": 15,
    "new_balance": 145,
    "message": "Points earned successfully"
}
```

**Earning Rate:** 1 point per R10 spent (10% conversion)

### Redeem Points
```
POST /api/loyalty/redeem
Authorization: Bearer {token}

{
    "user_id": "user_123456",
    "service_type": "ticket",
    "quantity": 1
}

Response:
{
    "success": true,
    "points_redeemed": 100,
    "new_balance": 45,
    "voucher_code": "ABC123XYZ",
    "valid_for_days": 30,
    "message": "Redemption successful"
}
```

### Get Loyalty Balance
```
GET /api/loyalty/balance/{user_id}
Authorization: Bearer {token}

Response:
{
    "success": true,
    "user_id": "user_123456",
    "balance": 145,
    "equivalent_value": "R145.00",
    "next_reward": "Free ticket at 100 points"
}
```

### Get Available Rewards
```
GET /api/loyalty/rewards

Response:
{
    "success": true,
    "rewards": {
        "ticket": {
            "points_required": 100,
            "description": "1 free single ticket",
            "value": "R48.50"
        },
        "restaurant": {
            "points_required": 50,
            "description": "R50 restaurant voucher",
            "value": "R50.00"
        },
        "grocery": {
            "points_required": 50,
            "description": "R50 grocery voucher",
            "value": "R50.00"
        },
        "airtime": {
            "points_required": 20,
            "description": "R20 airtime",
            "value": "R20.00"
        },
        "data": {
            "points_required": 30,
            "description": "500MB data bundle",
            "value": "R30.00"
        }
    }
}
```

---

## Transit & Real-Time ETA

### Get Live ETA for All Stops
```
POST /api/transit/eta/all-stops
Authorization: Bearer {token}

{
    "route_id": "route_001",
    "current_location_index": 3
}

Response:
{
    "success": true,
    "route_id": "route_001",
    "vehicle_id": "BUS-001",
    "vehicle_status": "in_transit",
    "current_delay_minutes": 2,
    "stops": [
        {
            "station_index": 3,
            "station_name": "Main Station",
            "arrival_eta": "2024-01-20T10:35:00",
            "arrival_time_minutes": 5,
            "distance_km": 2.3,
            "traffic_condition": "light",
            "crowding_level": "moderate"
        },
        {
            "station_index": 4,
            "station_name": "Central Hub",
            "arrival_eta": "2024-01-20T10:42:00",
            "arrival_time_minutes": 12,
            "distance_km": 4.1,
            "traffic_condition": "moderate",
            "crowding_level": "full"
        }
    ]
}
```

### Start Live Tracking
```
POST /api/transit/tracking/start
Authorization: Bearer {token}

{
    "route_id": "route_001",
    "vehicle_id": "BUS-001"
}

Response:
{
    "success": true,
    "tracking_id": "track_123456",
    "message": "Live tracking initiated"
}
```

### Update Vehicle Location
```
PUT /api/transit/tracking/{tracking_id}/location
Authorization: Bearer {token}

{
    "latitude": -25.7589,
    "longitude": 28.2293,
    "station_index": 5,
    "status": "in_transit"
}

Response:
{
    "success": true,
    "message": "Location updated successfully"
}
```

---

## Error Handling

### Standard Error Responses

**400 Bad Request:**
```json
{
    "error": "Missing required fields",
    "fields": ["amount", "currency"]
}
```

**401 Unauthorized:**
```json
{
    "error": "Missing authorization token"
}
```

**404 Not Found:**
```json
{
    "error": "Resource not found",
    "resource_id": "card_123456"
}
```

**429 Too Many Requests:**
```json
{
    "error": "Rate limit exceeded",
    "retry_after": 60
}
```

**500 Internal Server Error:**
```json
{
    "error": "Internal server error",
    "timestamp": "2024-01-20T10:30:00"
}
```

---

## Rate Limiting

- **Standard endpoints:** 100 requests/minute per user
- **Payment endpoints:** 10 requests/minute per user
- **Authentication endpoints:** 5 requests/minute per IP

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

---

## Testing

### Sample cURL Commands

**Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password_hash": "hashed_password"
  }'
```

**Book Ticket:**
```bash
curl -X POST http://localhost:5000/api/tickets/book \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123456",
    "route_id": "route_001",
    "start_station": "Main Station",
    "end_station": "Airport",
    "ticket_type": "single",
    "price": 48.50
  }'
```

**Place Restaurant Order:**
```bash
curl -X POST http://localhost:5000/api/restaurants/order/place \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123456",
    "restaurant_id": "rest_001",
    "items": [{"item_id": "item_001", "quantity": 1}],
    "delivery_address": {"lat": -25.7589, "lon": 28.2293}
  }'
```

---

**Last Updated:** January 20, 2024  
**Version:** 1.0  
**Status:** Production Ready
