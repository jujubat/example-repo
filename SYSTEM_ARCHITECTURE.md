# System Architecture & User Flows

## 1. SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER (Frontend)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Login Page (login.html)                               │    │
│  │  ├─ Signup Form                                        │    │
│  │  │  ├─ Name, Email, Phone                             │    │
│  │  │  └─ Password (min 8 chars)                         │    │
│  │  └─ Login Form                                         │    │
│  │     ├─ Email                                           │    │
│  │     └─ Password                                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│           ↓                                    ↓                 │
│  ┌────────────────────┐        ┌──────────────────────┐         │
│  │  Main App          │        │  Admin Dashboard     │         │
│  │  (index.html)      │        │  (dashboard.html)    │         │
│  │  ├─ Weather        │        │  ├─ Pending Apps    │         │
│  │  ├─ Routes         │        │  ├─ User List       │         │
│  │  ├─ Cards          │        │  └─ Role Manager    │         │
│  │  └─ Settings       │        └──────────────────────┘         │
│  └────────────────────┘                                          │
│           ↓ API Calls (with JWT Token)                          │
└─────────────────────────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FLASK SERVER (Backend)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Authentication Endpoints                              │    │
│  │  POST /api/auth/signup     → user_manager.create_user  │    │
│  │  POST /api/auth/login      → user_manager.authenticate │    │
│  │  POST /api/auth/verify     → JWT verification          │    │
│  └─────────────────────────────────────────────────────────┘    │
│           ↓                                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Admin Endpoints (@admin_required decorator)           │    │
│  │  GET  /api/admin/pending-approvals                     │    │
│  │  POST /api/admin/approve-account                       │    │
│  │  POST /api/admin/reject-account                        │    │
│  │  GET  /api/admin/users                                 │    │
│  │  POST /api/admin/set-user-role                         │    │
│  │  GET  /api/admin/roles                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│           ↓                                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  UserManager (user_management.py)                      │    │
│  │  ├─ Users Dictionary (In-Memory Storage)               │    │
│  │  │  ├─ user_id → user_data                            │    │
│  │  │  ├─ Roles (4 types)                                │    │
│  │  │  └─ Capabilities per role                          │    │
│  │  └─ Methods                                            │    │
│  │     ├─ create_user()                                  │    │
│  │     ├─ authenticate_user()                            │    │
│  │     ├─ approve_account()                              │    │
│  │     ├─ set_user_role()                                │    │
│  │     └─ check_auto_activate()                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. USER SIGNUP FLOW

```
User Clicks "Sign Up"
         ↓
    Form Displayed
    ├─ Full Name
    ├─ Email
    ├─ Phone
    ├─ Password (min 8 chars)
    └─ Confirm Password
         ↓
    Frontend Validation
    ├─ Email format check
    ├─ Password strength
    └─ Password match
         ↓
    POST /api/auth/signup
    ├─ name
    ├─ email
    ├─ phone
    └─ password
         ↓
    ┌─────────────────────────────────────┐
    │ Is email batwiineltdgroup@gmail.com?│
    └─────────────────────────────────────┘
         ↓              ↓
        YES            NO
         ↓              ↓
    ┌─────────────┐  ┌──────────────┐
    │ Super Admin │  │ Regular User │
    │ Auto-Active │  │ Pending      │
    └─────────────┘  └──────────────┘
         ↓              ↓
    ✅ Ready to Login   ⏳ Awaiting Approval
```

---

## 3. LOGIN FLOW

```
User Enters Email & Password
         ↓
Frontend Validation
├─ Email format
└─ Password not empty
         ↓
POST /api/auth/login
├─ email
└─ password
         ↓
Backend: authenticate_user()
├─ Find user by email
├─ Compare password hash
└─ Check status
         ↓
    ┌──────────────────────────┐
    │ What is account status?  │
    └──────────────────────────┘
         ↓        ↓        ↓
     active   pending   rejected
         ↓        ↓        ↓
      ✅OK    ❌Wait     ❌Denied
         ↓        ↓        ↓
     Generate  Show      Show
     JWT Token Message   Message
         ↓
    Save JWT Token
    Save User Object
    Redirect to:
    ├─ /dashboard (if admin)
    └─ / (if regular user)
```

---

## 4. ACCOUNT APPROVAL WORKFLOW

```
PENDING ACCOUNT CREATED
         ↓
┌─────────────────────────────────────┐
│  Admin Logs In & Views Dashboard    │
└─────────────────────────────────────┘
         ↓
   Pending Approvals Tab
   Shows:
   ├─ User Name
   ├─ Email
   ├─ Phone
   ├─ Applied Date
   └─ Details Completed: 3/4
         ↓
  ┌──────────────────────────────┐
  │  Admin Reviews Account        │
  └──────────────────────────────┘
         ↓        ↓
     APPROVE  REJECT
         ↓        ↓
    ┌────────┐  ┌─────────────────┐
    │Status: │  │Reason Prompt:   │
    │active  │  │"Incomplete info"│
    ├────────┤  └─────────────────┘
    │Role:   │        ↓
    │user    │  Status: rejected
    │        │  ✗ Cannot login
    │User can│
    │now     │
    │login ✅│
    └────────┘
```

---

## 5. AUTO-ACTIVATION FLOW

```
USER UPDATES PROFILE
├─ Uploads profile picture
├─ Enters address
└─ Submits
         ↓
POST /api/user/update-details
         ↓
check_auto_activate()
         ↓
   ┌──────────────────────────────┐
   │ Check All Required Details:  │
   ├──────────────────────────────┤
   │ ✓ Full Name                  │
   │ ✓ Email Address              │
   │ ✓ Phone Number               │
   │ ✓ Address                    │
   │ ✓ All required = 100%        │
   └──────────────────────────────┘
         ↓
    Status: active
    ✅ User can access app
    ✅ Can use all features
```

---

## 6. ADMIN DASHBOARD FLOW

```
┌─────────────────────────────────────┐
│  Admin Logs In (role: admin/super)  │
└─────────────────────────────────────┘
         ↓
Navigate to /dashboard
         ↓
    Check Role & Permissions
         ↓
     ┌─────────────────────────────┐
     │ Is user admin/super_admin?  │
     └─────────────────────────────┘
         ↓              ↓
        YES            NO
         ↓              ↓
    Load Dashboard  Access Denied
         ↓
    ┌─────────────────────────────────┐
    │  Three Main Tabs                 │
    ├─────────────────────────────────┤
    │ 1. Pending Approvals            │
    │    ├─ [✓ Approve] [✗ Reject]    │
    │    └─ Updates live              │
    │                                 │
    │ 2. Manage Users                 │
    │    ├─ Table of all users        │
    │    ├─ [Edit] button per user    │
    │    └─ Change roles              │
    │                                 │
    │ 3. Manage Roles                 │
    │    ├─ List of 4 roles           │
    │    ├─ Super Admin capabilities  │
    │    ├─ Admin capabilities        │
    │    ├─ Moderator capabilities    │
    │    └─ User capabilities         │
    └─────────────────────────────────┘
```

---

## 7. ROLE CHANGE FLOW (Super Admin Only)

```
SUPER ADMIN IN DASHBOARD
         ↓
Manage Users Tab
         ↓
Click Edit Button (for a user)
         ↓
   Prompt for new role:
   ├─ super_admin
   ├─ admin
   ├─ moderator
   └─ user
         ↓
POST /api/admin/set-user-role
├─ user_id
└─ role
         ↓
Backend: set_user_role()
├─ Validate: Only super_admin can change roles
├─ Log change: from_role → to_role
├─ Update user.role
├─ Update user.capabilities
└─ Update role_change_log
         ↓
Response: Success
├─ Previous role: user
├─ New role: admin
└─ Changed at: timestamp
         ↓
    User reloads dashboard
    ✅ User now sees admin features
    ✅ Can access admin endpoints
    ✅ Change logged in history
```

---

## 8. TOKEN VERIFICATION FLOW

```
CLIENT REQUESTS ADMIN ENDPOINT
  GET /api/admin/users
         ↓
Include Header:
Authorization: Bearer <JWT_TOKEN>
         ↓
SERVER RECEIVES REQUEST
         ↓
@admin_required decorator
         ↓
Extract Token from Header
         ↓
Decode JWT
├─ Verify signature
├─ Check expiration
└─ Get user_id, email, role
         ↓
    ┌────────────────────────┐
    │ Is role admin/super?   │
    └────────────────────────┘
         ↓              ↓
        YES            NO
         ↓              ↓
    Execute       Return 403
    Endpoint    "Admin access
    ✅          required"
                ❌
         ↓
    Return Response
    {
      "success": true,
      "users": [...]
    }
```

---

## 9. CAPABILITY CHECK FLOW

```
USER TRIES TO ACCESS FEATURE
         ↓
Frontend checks localStorage.user.role
         ↓
    ┌──────────────────────────────┐
    │ Does user have capability?   │
    └──────────────────────────────┘
         ↓        ↓
        YES      NO
         ↓        ↓
    Show      Hide/Disable
    Feature   Feature
         ↓
    If API needed:
    POST /api/protected/endpoint
         ↓
    Backend checks:
    has_capability(user_id, "required_cap")
         ↓
    ┌──────────────────────┐
    │ Has capability?      │
    └──────────────────────┘
         ↓        ↓
        YES      NO
         ↓        ↓
    Execute   Return 403
    Feature   "Access
    ✅        Denied"
              ❌
```

---

## 10. DATA STORAGE STRUCTURE

```
IN-MEMORY USER STORAGE

{
  "uuid-1": {
    "user_id": "uuid-1",
    "name": "Super Admin",
    "email": "batwiineltdgroup@gmail.com",
    "phone": "+1234567890",
    "password_hash": "abc123def456...",
    "role": "super_admin",
    "status": "active",
    "account_verified": true,
    "created_at": "2026-01-17T10:00:00",
    "approved_at": "2026-01-17T10:00:00",
    "approved_by": "system",
    "details_completed": {
      "name": true,
      "email": true,
      "phone": true,
      "address": true,
      "profile_picture": false
    },
    "role_change_log": []
  },
  "uuid-2": {
    "user_id": "uuid-2",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+9876543210",
    "password_hash": "xyz789abc123...",
    "role": "admin",
    "status": "active",
    "account_verified": true,
    "created_at": "2026-01-17T11:00:00",
    "approved_at": "2026-01-17T12:00:00",
    "approved_by": "uuid-1",
    "details_completed": {
      "name": true,
      "email": true,
      "phone": true,
      "address": true,
      "profile_picture": true
    },
    "role_change_log": [
      {
        "from": "user",
        "to": "admin",
        "changed_at": "2026-01-17T12:00:00",
        "changed_by": "uuid-1"
      }
    ]
  },
  "uuid-3": {
    "user_id": "uuid-3",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+1111111111",
    "password_hash": "pqr456stu789...",
    "role": "user",
    "status": "pending",
    "account_verified": false,
    "created_at": "2026-01-17T13:00:00",
    "details_completed": {
      "name": true,
      "email": true,
      "phone": true,
      "address": false,
      "profile_picture": false
    }
  }
}

ROLE DEFINITIONS

{
  "super_admin": {
    "name": "Super Admin",
    "capabilities": [
      "view_users", "create_users", "edit_users", "delete_users",
      "manage_roles", "approve_accounts", "view_admin_logs",
      "manage_weather_api", "manage_cards", "system_settings"
    ]
  },
  "admin": {
    "name": "Admin",
    "capabilities": [
      "view_users", "edit_users", "approve_accounts",
      "view_admin_logs", "manage_cards"
    ]
  },
  "moderator": {
    "name": "Moderator",
    "capabilities": ["view_users", "manage_cards"]
  },
  "user": {
    "name": "Regular User",
    "capabilities": [
      "view_profile", "edit_profile", "use_weather", "use_cards"
    ]
  }
}
```

---

## 11. JWT TOKEN STRUCTURE

```
HEADER
{
  "alg": "HS256",
  "typ": "JWT"
}

PAYLOAD
{
  "user_id": "uuid-string",
  "email": "user@example.com",
  "role": "admin",
  "exp": 1705416000  (Unix timestamp, 24 hours later)
}

SIGNATURE
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  "tap_trip_secret_key_2024"
)

FINAL TOKEN (example)
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXVpZCIsImVtYWlsIjoiamR
vZUBlbWFpbC5jb20iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3MDU0MTYwMDB9.abc123...
```

---

## 12. ERROR FLOW

```
USER ATTEMPTS INVALID ACTION
         ↓
    ┌──────────────────────────────┐
    │ What went wrong?             │
    └──────────────────────────────┘
         ↓        ↓        ↓        ↓
    Missing   Invalid   Expired   No Access
    Fields    Token     Token     Rights
         ↓        ↓        ↓        ↓
    400      401      401      403
    Bad      Unauth   Unauth   Forbidden
    Request
         ↓        ↓        ↓        ↓
    Response with error message
    {
      "success": false,
      "message": "Error description"
    }
         ↓
    Frontend shows error
    to user
         ↓
    User can retry
    or try different action
```

---

This architecture provides a scalable, secure authentication system ready for production use!
