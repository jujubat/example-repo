# PHASE 3 INTEGRATION GUIDE
## Adding Advanced Features to Flask App

---

## INTEGRATION CHECKLIST

- [ ] Import new modules in app.py
- [ ] Initialize new systems at app startup
- [ ] Add database collections to Firestore
- [ ] Add API routes for new endpoints
- [ ] Configure authentication middleware
- [ ] Test all endpoints
- [ ] Deploy to production
- [ ] Set up monitoring and alerts

---

## STEP 1: Update Requirements

Add these to `requirements.txt`:

```
firebase-admin>=6.0.0
flask-cors>=4.0.0
python-dotenv>=1.0.0
reportlab>=4.0.0
PyPDF2>=3.0.0
```

---

## STEP 2: Import in app.py

```python
from batuma_gprs_weather.admin.advanced_reporting import (
    AdvancedPurchaseReporter, PurchaseRecord, ApprovalStatus
)
from batuma_gprs_weather.admin.super_admin_dashboard import (
    SuperAdminDashboard, BankDetailChangeRequest, StationManagementRequest
)
from batuma_gprs_weather.transit.bus_management import (
    NationalBusManagementSystem, BusFleet, BusRoute
)
from batuma_gprs_weather.transit.route_upload import (
    RouteUploadManager, PDFRouteParser
)
```

---

## STEP 3: Initialize Systems at Startup

Add to app startup (in `app.py` `__init__` or `__main__`):

```python
# Initialize advanced reporting system
app.advanced_reporter = AdvancedPurchaseReporter()

# Initialize super admin dashboard
# (will be instantiated per super admin login)
app.super_admin_instances = {}

# Initialize national bus management
app.bus_management = NationalBusManagementSystem()

# Initialize route upload manager
app.route_upload = RouteUploadManager()

logger.info("Phase 3 systems initialized successfully")
```

---

## STEP 4: Add Super Admin API Routes

Create `batuma_gprs_weather/routes/super_admin_routes.py`:

```python
from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime, timedelta
from batuma_gprs_weather.admin.super_admin_dashboard import SuperAdminDashboard
from batuma_gprs_weather.admin.advanced_reporting import AdvancedPurchaseReporter

super_admin_bp = Blueprint('super_admin', __name__, url_prefix='/api/super-admin')

# Middleware to verify super admin role
def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        # Verify JWT token and super admin role
        # Check if user has SUPER_ADMIN role
        if not has_super_admin_role(token):
            return jsonify({'error': 'Super admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# PURCHASE TRACKING ENDPOINTS

@super_admin_bp.route('/purchases/minute/<date>/<time>', methods=['GET'])
@super_admin_required
def get_minute_purchases(date, time):
    """Get purchases for specific minute"""
    customer_id = request.args.get('customer_id')
    start_time = datetime.fromisoformat(f"{date}T{time}:00")
    
    from flask import current_app
    report = current_app.advanced_reporter.get_minute_report(
        customer_id, start_time
    )
    return jsonify(report), 200

@super_admin_bp.route('/purchases/hourly/<date>/<hour>', methods=['GET'])
@super_admin_required
def get_hourly_purchases(date, hour):
    """Get purchases for specific hour"""
    customer_id = request.args.get('customer_id')
    start_date = datetime.fromisoformat(date)
    
    from flask import current_app
    report = current_app.advanced_reporter.get_hourly_report(
        customer_id, start_date
    )
    return jsonify(report), 200

@super_admin_bp.route('/purchases/daily/<date>', methods=['GET'])
@super_admin_required
def get_daily_purchases(date):
    """Get daily purchase report"""
    customer_id = request.args.get('customer_id')
    start_date = datetime.fromisoformat(date)
    
    from flask import current_app
    report = current_app.advanced_reporter.get_daily_report(
        customer_id, start_date
    )
    return jsonify(report), 200

@super_admin_bp.route('/purchases/monthly/<date>', methods=['GET'])
@super_admin_required
def get_monthly_purchases(date):
    """Get monthly purchase report"""
    customer_id = request.args.get('customer_id')
    year_month = datetime.fromisoformat(f"{date}-01")
    
    from flask import current_app
    report = current_app.advanced_reporter.get_monthly_report(
        customer_id, year_month
    )
    return jsonify(report), 200

@super_admin_bp.route('/purchases/yearly/<year>', methods=['GET'])
@super_admin_required
def get_yearly_purchases(year):
    """Get yearly purchase report"""
    customer_id = request.args.get('customer_id')
    start_year = int(year)
    
    from flask import current_app
    report = current_app.advanced_reporter.get_yearly_report(
        customer_id, start_year
    )
    return jsonify(report), 200

@super_admin_bp.route('/purchases/flagged', methods=['GET'])
@super_admin_required
def get_flagged_purchases():
    """Get all flagged transactions"""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now() - timedelta(days=days)
    
    from flask import current_app
    flagged = current_app.advanced_reporter.get_all_flagged_transactions(
        start_date
    )
    return jsonify({'flagged': flagged}), 200

@super_admin_bp.route('/customer/<customer_id>/comprehensive', methods=['GET'])
@super_admin_required
def get_customer_comprehensive(customer_id):
    """Get comprehensive customer analysis"""
    days = request.args.get('days', 90, type=int)
    start_date = datetime.now() - timedelta(days=days)
    
    from flask import current_app
    report = current_app.advanced_reporter.get_comprehensive_customer_report(
        customer_id, start_date
    )
    return jsonify(report), 200

# BANK APPROVAL ENDPOINTS

@super_admin_bp.route('/bank-requests/pending', methods=['GET'])
@super_admin_required
def get_pending_bank_requests():
    """Get pending bank change requests"""
    admin_id = get_super_admin_id_from_token()
    
    # Get from database
    db = get_firestore_db()
    requests = db.collection('approval_workflows')\
        .where('request_type', '==', 'bank')\
        .where('status', '==', 'pending')\
        .stream()
    
    return jsonify({
        'pending': [req.to_dict() for req in requests]
    }), 200

@super_admin_bp.route('/bank-requests/<request_id>/approve', methods=['POST'])
@super_admin_required
def approve_bank_request(request_id):
    """Approve bank detail change"""
    data = request.get_json()
    notes = data.get('notes')
    admin_phone = get_super_admin_phone_from_token()
    
    # Update in database
    db = get_firestore_db()
    db.collection('approval_workflows').document(request_id).update({
        'status': 'approved',
        'approved_by_phone': admin_phone,
        'approved_at': datetime.now().isoformat(),
        'notes': notes
    })
    
    # Log to audit trail
    db.collection('audit_trail').add({
        'timestamp': datetime.now().isoformat(),
        'action': 'bank_request_approved',
        'request_id': request_id,
        'admin_phone': admin_phone,
        'notes': notes
    })
    
    return jsonify({'status': 'approved', 'request_id': request_id}), 200

@super_admin_bp.route('/bank-requests/<request_id>/reject', methods=['POST'])
@super_admin_required
def reject_bank_request(request_id):
    """Reject bank detail change"""
    data = request.get_json()
    reason = data.get('reason')
    admin_phone = get_super_admin_phone_from_token()
    
    db = get_firestore_db()
    db.collection('approval_workflows').document(request_id).update({
        'status': 'rejected',
        'rejected_by_phone': admin_phone,
        'rejected_at': datetime.now().isoformat(),
        'rejection_reason': reason
    })
    
    # Log
    db.collection('audit_trail').add({
        'timestamp': datetime.now().isoformat(),
        'action': 'bank_request_rejected',
        'request_id': request_id,
        'admin_phone': admin_phone,
        'reason': reason
    })
    
    return jsonify({'status': 'rejected', 'request_id': request_id}), 200

# FLEET MANAGEMENT ENDPOINTS

@super_admin_bp.route('/fleet/company/register', methods=['POST'])
@super_admin_required
def register_bus_company():
    """Register new bus company"""
    data = request.get_json()
    
    from flask import current_app
    company = current_app.bus_management.register_company(
        company_name=data['company_name'],
        company_phone=data['company_phone'],
        company_email=data['company_email'],
        hq_province=data['hq_province'],
        license_number=data['license_number']
    )
    
    # Save to database
    db = get_firestore_db()
    db.collection('transit_companies').document(company['company_id']).set(company)
    
    return jsonify(company), 201

@super_admin_bp.route('/fleet/bus/add', methods=['POST'])
@super_admin_required
def register_bus():
    """Register new bus"""
    data = request.get_json()
    
    from flask import current_app
    bus = current_app.bus_management.add_bus(
        company_id=data['company_id'],
        registration_number=data['registration_number'],
        bus_type=data['bus_type'],
        manufacturer=data['manufacturer'],
        model=data['model'],
        year=data['year'],
        seating_capacity=data['seating_capacity'],
        driver_names=data.get('driver_names', []),
        driver_phones=data.get('driver_phones', [])
    )
    
    # Save to database
    db = get_firestore_db()
    db.collection('bus_fleet').document(bus.bus_id).set(bus.to_dict())
    
    return jsonify(bus.to_dict()), 201

@super_admin_bp.route('/fleet/summary', methods=['GET'])
@super_admin_required
def get_fleet_summary():
    """Get national fleet summary"""
    from flask import current_app
    summary = current_app.bus_management.get_fleet_summary()
    return jsonify(summary), 200

@super_admin_bp.route('/fleet/province/<province>', methods=['GET'])
@super_admin_required
def get_province_fleet(province):
    """Get fleet for specific province"""
    from flask import current_app
    fleet = current_app.bus_management.get_fleet_by_province(province)
    return jsonify(fleet), 200

# ROUTE UPLOAD ENDPOINTS

@super_admin_bp.route('/routes/upload/pdf', methods=['POST'])
@super_admin_required
def upload_pdf_route():
    """Upload and parse PDF route"""
    pdf_content = request.form.get('pdf_content')
    admin_phone = get_super_admin_phone_from_token()
    admin_name = get_super_admin_name_from_token()
    
    from flask import current_app
    result = current_app.route_upload.upload_pdf_route(
        pdf_content, admin_name, admin_phone
    )
    
    return jsonify(result.to_dict()), 201

@super_admin_bp.route('/routes/pending', methods=['GET'])
@super_admin_required
def get_pending_routes():
    """Get routes pending import"""
    from flask import current_app
    pending = current_app.route_upload.get_pending_imports()
    return jsonify({'pending': pending}), 200

@super_admin_bp.route('/routes/import/confirm', methods=['POST'])
@super_admin_required
def confirm_route_import():
    """Confirm route import"""
    data = request.get_json()
    result_id = data['result_id']
    admin_phone = get_super_admin_phone_from_token()
    admin_name = get_super_admin_name_from_token()
    
    from flask import current_app
    import_result = current_app.route_upload.confirm_import(
        result_id, admin_name, admin_phone
    )
    
    return jsonify(import_result), 200

# DASHBOARD

@super_admin_bp.route('/dashboard/summary', methods=['GET'])
@super_admin_required
def get_super_admin_dashboard():
    """Get super admin dashboard"""
    admin_phone = get_super_admin_phone_from_token()
    
    db = get_firestore_db()
    
    # Get pending counts
    pending_banks = db.collection('approval_workflows')\
        .where('request_type', '==', 'bank')\
        .where('status', '==', 'pending').count().get()[0][0].value
    
    pending_stations = db.collection('approval_workflows')\
        .where('request_type', '==', 'station')\
        .where('status', '==', 'pending').count().get()[0][0].value
    
    # Get recent activity
    recent = db.collection('audit_trail')\
        .where('admin_phone', '==', admin_phone)\
        .order_by('timestamp', direction='DESCENDING')\
        .limit(10).stream()
    
    return jsonify({
        'pending': {
            'bank_changes': pending_banks,
            'station_changes': pending_stations,
            'total': pending_banks + pending_stations
        },
        'recent_activity': [doc.to_dict() for doc in recent],
        'timestamp': datetime.now().isoformat()
    }), 200
```

---

## STEP 5: Register Routes in app.py

```python
from batuma_gprs_weather.routes.super_admin_routes import super_admin_bp

app.register_blueprint(super_admin_bp)
```

---

## STEP 6: Add Firestore Security Rules

Update `firestore.rules`:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Super admin only collections
    match /approval_workflows/{document=**} {
      allow read: if request.auth.token.role == 'super_admin';
      allow write: if request.auth.token.role == 'super_admin';
    }
    
    match /audit_trail/{document=**} {
      allow read: if request.auth.token.role == 'super_admin';
      allow write: if request.auth.token.role == 'super_admin';
    }
    
    match /bank_detail_changes/{document=**} {
      allow read: if request.auth.token.role == 'super_admin';
      allow write: if request.auth.token.role == 'super_admin';
    }
    
    match /bus_fleet/{document=**} {
      allow read: if request.auth.token.role in ['admin', 'super_admin'];
      allow write: if request.auth.token.role == 'super_admin';
    }
    
    match /transit_companies/{document=**} {
      allow read: if request.auth != null;
      allow write: if request.auth.token.role == 'super_admin';
    }
    
    match /route_uploads/{document=**} {
      allow read: if request.auth.token.role == 'super_admin';
      allow write: if request.auth.token.role == 'super_admin';
    }
    
    match /purchase_records/{document=**} {
      allow read: if request.auth.token.role in ['admin', 'super_admin'];
      allow write: if request.auth != null;
    }
  }
}
```

---

## STEP 7: Update Requirements

Add to `requirements.txt`:

```txt
# Advanced Reporting
reportlab==4.0.9  # PDF generation
PyPDF2==3.0.1     # PDF parsing

# Bus Management
firebase-admin==6.1.0

# Route Parsing
python-dotenv==1.0.0

# Testing
pytest==7.4.0
pytest-cov==4.1.0
```

---

## STEP 8: Test Endpoints

```bash
# Test super admin login
curl -X POST http://localhost:5000/api/super-admin/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "+27123456789", "password": "password"}'

# Test minute report
curl http://localhost:5000/api/super-admin/purchases/minute/2024-01-15/14:32 \
  -H "Authorization: Bearer {jwt_token}" \
  -H "X-Customer-ID: CUST_123"

# Test bus registration
curl -X POST http://localhost:5000/api/super-admin/fleet/bus/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {jwt_token}" \
  -d '{
    "company_id": "CMP_001",
    "registration_number": "MQ 05 CD",
    "bus_type": "long_distance",
    "manufacturer": "Volvo",
    "model": "B11R",
    "year": 2023,
    "seating_capacity": 52,
    "driver_names": ["John Smith"],
    "driver_phones": ["+27111111111"]
  }'

# Test route upload
curl -X POST http://localhost:5000/api/super-admin/routes/upload/pdf \
  -H "Authorization: Bearer {jwt_token}" \
  -F "pdf_content=@route.pdf"
```

---

## STEP 9: Set Up Monitoring

Add to monitoring config:

```yaml
alerts:
  - name: PurchaseApprovalDelay
    threshold: 300  # seconds
    metric: approval_processing_time
    
  - name: FleetRegistrationErrors
    threshold: 5
    metric: bus_registration_failures
    
  - name: RouteUploadFailures
    threshold: 3
    metric: route_parse_errors
    
  - name: SuperAdminActivityLog
    log: audit_trail
    level: WARNING
```

---

## STEP 10: Deploy

```bash
# 1. Build and test locally
pytest tests/

# 2. Deploy to staging
gcloud app deploy --version=staging

# 3. Run smoke tests
python tests/smoke_tests.py

# 4. Deploy to production
gcloud app deploy

# 5. Monitor
gcloud app logs read --limit=100
```

---

## HELPER FUNCTIONS TO ADD

Add these utilities:

```python
# In security.py or utils.py

def get_super_admin_id_from_token():
    """Extract super admin ID from JWT token"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    decoded = decode_jwt_token(token)
    return decoded.get('admin_id')

def get_super_admin_phone_from_token():
    """Extract super admin phone from JWT token"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    decoded = decode_jwt_token(token)
    return decoded.get('phone')

def get_super_admin_name_from_token():
    """Extract super admin name from JWT token"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    decoded = decode_jwt_token(token)
    return decoded.get('name')

def has_super_admin_role(token):
    """Verify super admin role"""
    try:
        decoded = decode_jwt_token(token)
        return decoded.get('role') == 'super_admin'
    except:
        return False

def get_firestore_db():
    """Get Firestore database instance"""
    import firebase_admin
    return firebase_admin.firestore.client()
```

---

## VERIFICATION CHECKLIST

After integration:

- [ ] All 5 new modules imported without errors
- [ ] Firestore collections created and indexed
- [ ] API endpoints responding on correct paths
- [ ] Super admin authentication working
- [ ] Purchase minute reports generating
- [ ] Bank approval workflow functioning
- [ ] Bus registration creating records
- [ ] Route PDF parsing working
- [ ] Audit trail logging all actions
- [ ] Monitoring alerts configured
- [ ] Load testing passed (1000+ concurrent)
- [ ] Security rules enforced
- [ ] GDPR compliance verified
- [ ] Backup procedures tested

---

## TROUBLESHOOTING

### Issue: Module import errors
```
Solution: Ensure __init__.py files exist in all directories
```

### Issue: Firestore permissions denied
```
Solution: Update security rules to allow super_admin role
```

### Issue: PDF parsing fails
```
Solution: Ensure PDF format matches expected structure
```

### Issue: Route validation rejecting valid routes
```
Solution: Check provincial list against SA_PROVINCES constant
```

### Issue: Audit trail not logging
```
Solution: Verify Firestore write permissions in security rules
```

---

## SUPPORT

For integration support:
- Review `APP_ARCHITECTURE_COMPLETE.md` for detailed documentation
- Check `PHASE_3_DELIVERY_SUMMARY.md` for feature overview
- Review code comments for implementation details
- Run unit tests: `pytest tests/phase3/`

---

**Integration Status**: Ready  
**Estimated Time**: 4-6 hours  
**Difficulty**: Advanced  
**Requirements**: Firebase project, Flask app running, Firestore database
