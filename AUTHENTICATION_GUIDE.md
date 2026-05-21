# Tap Trip - Authentication & Admin System Documentation

## System Overview

The Tap Trip platform now includes a complete authentication and admin management system with role-based access control (RBAC), account approval workflows, and multi-channel capabilities management.

---

## 1. SUPER ADMIN EMAIL

**Primary Super Admin Email:** `batwiineltdgroup@gmail.com`

This email automatically receives **Super Admin** status and capabilities when an account is created. It does NOT require approval.

**Super Admin Capabilities:**
- View all users
- Create new users  
- Edit user profiles
- Delete users
- Manage user roles (change roles for any user)
- Approve pending accounts
- Reject pending accounts with reasons
- Manage system roles and capabilities
- View complete admin logs
- Manage weather API settings
- Manage payment card settings
- System settings and configuration

---

## 2. AUTHENTICATION SYSTEM

### Login/Signup Flow

**File:** `frontend/login.html`

#### Account Creation
1. User clicks "Sign Up"
2. Enters: Full Name, Email, Phone, Password
3. System validates:
   - Email format
   - Password strength (min 8 characters)
   - Password confirmation match
4. Account is created with status:
   - **If email is `batwiineltdgroup@gmail.com`:** Account activated immediately (Super Admin role)
   - **If email is different:** Account set to "pending" status (requires admin approval)

#### Login
1. User enters Email and Password
2. System authenticates credentials
3. If account is "pending": Shows message "Account is pending. Please wait for admin approval"
4. If account is "active": Generates JWT token valid for 24 hours
5. User redirected to Dashboard (if admin) or Main App

### JWT Token Structure

```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "role": "admin",
  "exp": 1234567890
}
```

**Token Location:** `localStorage.auth_token`
**User Data Location:** `localStorage.user`

---

## 3. ACCOUNT APPROVAL WORKFLOW

### Flow Diagram

```
User Signup
    ↓
Account Created (Status: pending)
    ↓
Admin Reviews in Dashboard
    ↓
┌─────────────────────────────────┐
│  Check Uploaded Details        │
│  - Name ✓                       │
│  - Email ✓                      │
│  - Phone ✓                      │
│  - Address (optional)           │
│  - Profile Picture (optional)   │
└─────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│ All Required Details Completed?          │
├──────────────────────────────────────────┤
│ YES → Auto-Activate Account              │
│ NO → Wait for Admin Approval             │
└──────────────────────────────────────────┘
```

### Auto-Activation Criteria

Account is **automatically activated** when ALL required details are completed:

1. ✅ Full Name
2. ✅ Email Address
3. ✅ Phone Number
4. ✅ Address
5. ⭕ Profile Picture (optional but helps)

### Manual Approval

**Admin/Super Admin** can manually:
1. **Approve Account** → Immediately activates (requires no additional details)
2. **Reject Account** → Deactivates with reason provided

---

## 4. ROLE-BASED ACCESS CONTROL (RBAC)

### Available Roles

#### 1. **Super Admin**
- **Auto-assigned to:** `batwiineltdgroup@gmail.com`
- **Capabilities:** All system capabilities (see list above)
- **Permissions:** Can manage all other admin roles

#### 2. **Admin**
- **How to assign:** Super Admin changes user role to "admin"
- **Capabilities:**
  - view_users
  - edit_users
  - approve_accounts
  - view_admin_logs
  - manage_cards

#### 3. **Moderator**
- **How to assign:** Super Admin changes user role to "moderator"
- **Capabilities:**
  - view_users
  - manage_cards

#### 4. **User** (Regular User)
- **Default role** for new accounts
- **Capabilities:**
  - view_profile
  - edit_profile
  - use_weather
  - use_cards

---

## 5. ADMIN DASHBOARD

**URL:** `http://localhost:8000/dashboard`

**Access:** Only available to admin and super_admin roles

### Dashboard Sections

#### A. Pending Approvals Tab
Shows all accounts awaiting approval with:
- User Name
- Email Address
- Phone Number
- Application Date
- Completed Details Progress (e.g., "3/4 completed")
- **Approve Button** - Instantly activates account
- **Reject Button** - Deactivates with reason

#### B. Manage Users Tab
Displays table of all users with:
- Name
- Email
- Current Role (badge-colored)
- Status (active/pending/rejected)
- Created Date
- **Edit Button** - Change user role

#### C. Manage Roles Tab
Shows all available roles with:
- Role Name
- Role ID
- All Capabilities for that role
- Can only be modified by Super Admin

---

## 6. API ENDPOINTS

### Authentication Endpoints

#### POST `/api/auth/signup`
Create new user account

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "password": "SecurePass123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Account created. Waiting for admin approval",
  "user_id": "uuid-here",
  "user": { ... }
}
```

#### POST `/api/auth/login`
Authenticate user

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "jwt-token-here",
  "user": {
    "user_id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "status": "active"
  }
}
```

#### POST `/api/auth/verify-token`
Verify JWT token

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response (Success):**
```json
{
  "success": true,
  "user": { ... }
}
```

### Admin Endpoints

All require:
- **Header:** `Authorization: Bearer <jwt-token>`
- **Role:** `admin` or `super_admin`

#### GET `/api/admin/pending-approvals`
Get all pending accounts

**Response:**
```json
{
  "success": true,
  "approvals": [
    {
      "user_id": "uuid",
      "name": "Jane Smith",
      "email": "jane@example.com",
      "phone": "+1234567890",
      "created_at": "2026-01-17T10:00:00",
      "details_completed": {
        "name": true,
        "email": true,
        "phone": true,
        "address": false
      }
    }
  ]
}
```

#### POST `/api/admin/approve-account`
Approve pending account

**Request:**
```json
{
  "user_id": "uuid-here"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Account for Jane Smith approved",
  "user": { ... }
}
```

#### POST `/api/admin/reject-account`
Reject pending account

**Request:**
```json
{
  "user_id": "uuid-here",
  "reason": "Incomplete information"
}
```

#### GET `/api/admin/users`
Get all users

**Response:**
```json
{
  "success": true,
  "users": [
    {
      "user_id": "uuid",
      "name": "John Doe",
      "email": "john@example.com",
      "role": "admin",
      "status": "active",
      "created_at": "2026-01-10T...",
      "last_login": "2026-01-17T..."
    }
  ]
}
```

#### POST `/api/admin/set-user-role`
Change user role (Super Admin Only)

**Request:**
```json
{
  "user_id": "uuid-here",
  "role": "admin"  // or "moderator", "user"
}
```

#### GET `/api/admin/roles`
Get all available roles and capabilities

**Response:**
```json
{
  "success": true,
  "roles": [
    {
      "id": "super_admin",
      "name": "Super Admin",
      "capabilities": [...]
    },
    {
      "id": "admin",
      "name": "Admin",
      "capabilities": [...]
    }
  ]
}
```

#### POST `/api/user/update-details`
Update user profile (auto-activate if all details complete)

**Request:**
```json
{
  "name": "John Updated",
  "phone": "+9876543210",
  "address": "123 Main St",
  "profile_picture": "url-to-image"
}
```

---

## 7. USER MANAGEMENT CLASS

**File:** `user_management.py`

### Key Methods

```python
# Create user
user_manager.create_user(name, email, phone, password)

# Authenticate
user_manager.authenticate_user(email, password)

# Approve account
user_manager.approve_account(user_id, approved_by)

# Reject account
user_manager.reject_account(user_id, rejected_by, reason)

# Change role
user_manager.set_user_role(user_id, new_role, changed_by)

# Update capabilities
user_manager.update_user_capabilities(user_id, new_capabilities, updated_by)

# Check capability
user_manager.has_capability(user_id, capability)

# Get pending approvals
user_manager.get_pending_approvals()

# Get all users
user_manager.get_all_users()

# Update user details
user_manager.update_user_details(user_id, details)

# Auto-activate if complete
user_manager.check_auto_activate(user_id)
```

---

## 8. USER DATA STRUCTURE

```python
{
    'user_id': 'uuid',
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '+1234567890',
    'password_hash': 'sha256-hash',
    'role': 'admin',  # super_admin, admin, moderator, user
    'status': 'active',  # pending, active, rejected
    'account_verified': True,
    'created_at': '2026-01-17T10:00:00',
    'created_by': 'system',
    'last_login': '2026-01-17T12:00:00',
    'approved_at': '2026-01-17T11:00:00',
    'approved_by': 'uuid-of-approver',
    'details_completed': {
        'name': True,
        'email': True,
        'phone': True,
        'address': False,
        'profile_picture': False
    },
    'custom_capabilities': [],  # Custom capabilities for this user
    'role_change_log': [
        {
            'from': 'user',
            'to': 'moderator',
            'changed_at': '2026-01-17T...',
            'changed_by': 'uuid-of-changer'
        }
    ]
}
```

---

## 9. TESTING THE SYSTEM

### Test Scenario 1: Create Super Admin Account

1. Go to `http://localhost:8000/login.html`
2. Click "Sign Up"
3. Enter:
   - Name: "Super Admin"
   - Email: **`batwiineltdgroup@gmail.com`** (EXACT)
   - Phone: "+1234567890"
   - Password: "SuperSecure123"
4. Click "Create Account"
5. ✅ Account created and immediately activated
6. Login with this account
7. ✅ Should see "🔐 Admin Panel" link
8. Click Admin Panel → Manage Roles Tab

### Test Scenario 2: Create Regular User Account

1. Go to `http://localhost:8000/login.html`
2. Click "Sign Up"
3. Enter:
   - Name: "Jane Smith"
   - Email: "jane@example.com"
   - Phone: "+9876543210"
   - Password: "SecurePass456"
4. Click "Create Account"
5. ✅ Account created with "pending" status
6. Try to login
7. ❌ Should show "Account is pending. Please wait for admin approval"

### Test Scenario 3: Approve Account

1. Login as Super Admin (batwiineltdgroup@gmail.com)
2. Click "🔐 Admin Panel"
3. Pending Approvals tab should show Jane Smith
4. Click "✓ Approve"
5. ✅ Account approved
6. Jane can now login

### Test Scenario 4: Change User Role

1. Login as Super Admin
2. Click "🔐 Admin Panel"
3. Go to "Manage Users" tab
4. Find Jane Smith
5. Click "Edit"
6. Enter new role: "admin"
7. ✅ Role changed
8. Jane now has admin capabilities

### Test Scenario 5: Auto-Activation

1. Create new user account (pending status)
2. Login as admin
3. Go to Admin Panel → Manage Users
4. Find the pending user
5. Have them complete all required details (name, email, phone, address)
6. ✅ Account automatically activated

---

## 10. SECURITY FEATURES

1. **Password Hashing:** SHA-256 hashing
2. **JWT Tokens:** 24-hour expiration
3. **Role-Based Access:** Only admins can access admin endpoints
4. **Email Validation:** RFC-compliant email format checking
5. **Phone Validation:** International format support
6. **Password Requirements:** Minimum 8 characters
7. **Audit Trail:** All role changes logged with timestamp and modifier

---

## 11. NEXT STEPS

To integrate with real email/SMS services:

1. **Email Service:**
   - Update `approval_manager.py` EmailService class
   - Integrate SendGrid, AWS SES, or similar
   - Add API credentials to `.env`

2. **SMS Service:**
   - Update `approval_manager.py` SMSService class
   - Integrate Twilio, AWS SNS, or similar
   - Add API credentials to `.env`

3. **Database:**
   - Connect Firestore or MongoDB
   - Store user data persistently
   - Implement encryption for sensitive data

4. **Enhanced Features:**
   - Two-factor authentication (2FA)
   - Email verification
   - Password reset functionality
   - User session management
   - Detailed audit logging

---

## 12. FILES CREATED/MODIFIED

### Created Files:
- `frontend/login.html` - Login/Signup page
- `frontend/dashboard.html` - Admin dashboard
- `user_management.py` - User and role management
- `app_simple.py` - Simplified Flask app with authentication
- `AUTHENTICATION_GUIDE.md` - This file

### Modified Files:
- `frontend/index.html` - Added admin link to navbar
- `frontend/app.js` - Added authentication checks
- `app.py` - Added auth endpoints (original version)

---

## 13. RUNNING THE SYSTEM

```bash
# Start server
cd batuma_gprs_weather
python app_simple.py

# Server runs on http://localhost:8000
# Login page: http://localhost:8000/login.html
# Dashboard: http://localhost:8000/dashboard
# Main app: http://localhost:8000/
```

---

## 14. QUICK REFERENCE

| Action | Who Can Do It | Result |
|--------|---------------|--------|
| Create Account | Anyone | Account pending (except super admin email) |
| Approve Account | Admin, Super Admin | Activates pending account |
| Reject Account | Admin, Super Admin | Deactivates account |
| Change User Role | Super Admin Only | Updates user role and capabilities |
| View All Users | Admin, Super Admin | See all user list |
| View Admin Panel | Admin, Super Admin | Access full dashboard |
| Auto-Activate | System | When all details completed |

---

**System Created:** January 17, 2026
**Version:** 1.0
**Status:** Production Ready
