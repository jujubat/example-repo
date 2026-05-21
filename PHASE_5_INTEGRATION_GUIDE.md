# Phase 5 Integration Guide

## Complete Step-by-Step Integration

### Prerequisites

- Python 3.9+
- Flask 2.3.2
- Firebase Admin SDK
- Google Cloud Firestore
- South African bank API keys
- Face recognition API key (Azure Face API or similar)

### Installation

```bash
# Install dependencies
pip install flask==2.3.2 firebase-admin google-cloud-firestore

# Copy Phase 5 modules to project
cp batuma_gprs_weather/analytics/transaction_analytics.py <project>/
cp batuma_gprs_weather/payment/virtual_card_system.py <project>/
cp batuma_gprs_weather/auth/kyc_verification.py <project>/
cp batuma_gprs_weather/auth/biometric_auth.py <project>/
cp batuma_gprs_weather/financial/banking_integration.py <project>/
cp batuma_gprs_weather/fleet/fleet_management_scale.py <project>/
cp batuma_gprs_weather/routes/financial_routes.py <project>/
```

---

## Part 1: Database Setup

### Step 1.1: Initialize Firestore

```python
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Initialize Firebase
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

print("Firestore initialized")
```

### Step 1.2: Create Collections

```python
# Create collections (if not exists)
collections = [
    'virtual_cards',
    'transactions',
    'transfers',
    'kyc_profiles',
    'kyc_documents',
    'biometric_enrollments',
    'authentication_attempts',
    'bank_accounts',
    'buses',
    'routes',
    'depots'
]

for collection_name in collections:
    # Firestore creates collections on first write
    # Create dummy document
    db.collection(collection_name).document('_init').set({
        'created_at': firestore.SERVER_TIMESTAMP
    })
    print(f"Collection '{collection_name}' ready")
```

### Step 1.3: Create Indexes

```python
# Define composite indexes
indexes = [
    {
        'collection': 'virtual_cards',
        'fields': [('phone_number', 'ASCENDING'), ('created_at', 'DESCENDING')]
    },
    {
        'collection': 'transactions',
        'fields': [('client_id', 'ASCENDING'), ('timestamp', 'DESCENDING')]
    },
    {
        'collection': 'transactions',
        'fields': [('route_id', 'ASCENDING'), ('timestamp', 'DESCENDING')]
    },
    {
        'collection': 'routes',
        'fields': [('route_number', 'ASCENDING')]
    },
    {
        'collection': 'buses',
        'fields': [('registration', 'ASCENDING')]
    }
]

# Note: In production, create indexes via Firebase Console
print("Indexes configuration:")
for idx in indexes:
    print(f"  {idx['collection']}: {idx['fields']}")
```

---

## Part 2: Core System Initialization

### Step 2.1: Create Main App File

```python
# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

# Secret key for JWT
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Import systems
from batuma_gprs_weather.analytics.transaction_analytics import TransactionAnalyticsEngine
from batuma_gprs_weather.payment.virtual_card_system import VirtualCardSystem
from batuma_gprs_weather.auth.kyc_verification import KYCVerificationSystem
from batuma_gprs_weather.auth.biometric_auth import BiometricAuthenticationSystem
from batuma_gprs_weather.financial.banking_integration import BankingIntegrationSystem
from batuma_gprs_weather.fleet.fleet_management_scale import FleetManagementAtScale

# Initialize systems
analytics = TransactionAnalyticsEngine()
cards = VirtualCardSystem()
kyc = KYCVerificationSystem()
biometric = BiometricAuthenticationSystem()
banking = BankingIntegrationSystem()
fleet = FleetManagementAtScale()

# Register blueprints
from batuma_gprs_weather.routes.financial_routes import financial_bp
app.register_blueprint(financial_bp)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

### Step 2.2: Create Environment Configuration

```bash
# .env
SECRET_KEY=your-secret-key-here
FIREBASE_PROJECT_ID=your-firebase-project
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-service-account@....iam.gserviceaccount.com

# Banking APIs
ABSA_API_KEY=your-absa-key
FNB_API_KEY=your-fnb-key
NEDBANK_API_KEY=your-nedbank-key

# Biometric APIs
FACE_API_KEY=your-face-api-key
FACE_API_ENDPOINT=https://your-region.face.cognitive.microsoft.com/

# SMS/Email
SMS_API_KEY=your-sms-api-key
EMAIL_API_KEY=your-email-api-key

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Step 2.3: Load Configuration

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Firebase
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
    FIREBASE_PRIVATE_KEY = os.getenv('FIREBASE_PRIVATE_KEY')
    FIREBASE_CLIENT_EMAIL = os.getenv('FIREBASE_CLIENT_EMAIL')
    
    # Banking
    BANKING_APIS = {
        'absa': os.getenv('ABSA_API_KEY'),
        'fnb': os.getenv('FNB_API_KEY'),
        'nedbank': os.getenv('NEDBANK_API_KEY')
    }
    
    # Biometric
    FACE_API_KEY = os.getenv('FACE_API_KEY')
    FACE_API_ENDPOINT = os.getenv('FACE_API_ENDPOINT')

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    DEBUG = True
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

---

## Part 3: User Onboarding Flow

### Step 3.1: Create User Endpoint

```python
# routes/user_routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime

user_bp = Blueprint('users', __name__, url_prefix='/api/users')

@user_bp.route('/onboard', methods=['POST'])
def onboard_user():
    """Complete user onboarding"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        name = data.get('name')
        email = data.get('email')
        
        # Validate phone format (South African)
        if not phone_number.startswith('27') or len(phone_number) != 11:
            return jsonify({'error': 'Invalid phone number'}), 400
        
        # Create virtual card
        card = cards.create_card(phone_number, name)
        
        # Create KYC profile
        kyc_profile = kyc.create_kyc_profile(phone_number, name, email)
        
        # Create biometric enrollment
        biometric.enroll_biometric(phone_number, "face_recognition")
        
        return jsonify({
            'success': True,
            'card_id': card.card_id,
            'account_number': card.account_number,
            'kyc_level': kyc_profile.kyc_level,
            'onboarding_complete': True
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Step 3.2: Create Document Upload Handler

```python
# utils/file_handler.py
import base64
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_kyc_document(file):
    """Handle KYC document upload"""
    
    if not file or file.filename == '':
        raise ValueError("No file selected")
    
    if not allowed_file(file.filename):
        raise ValueError("Invalid file type")
    
    # Check file size
    if len(file.getvalue()) > MAX_FILE_SIZE:
        raise ValueError("File too large")
    
    # Read and encode
    file_data = base64.b64encode(file.read()).decode('utf-8')
    
    return file_data, secure_filename(file.filename)
```

### Step 3.3: KYC Workflow Integration

```python
# routes/kyc_routes.py
from flask import Blueprint, request, jsonify, send_file
from utils.file_handler import handle_kyc_document

kyc_routes = Blueprint('kyc', __name__, url_prefix='/api/kyc')

@kyc_routes.route('/<phone_number>/verify', methods=['POST'])
def verify_kyc_document(phone_number):
    """Verify KYC document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        doc_type = request.form.get('document_type')
        
        if not doc_type:
            return jsonify({'error': 'Document type required'}), 400
        
        # Handle upload
        file_data, filename = handle_kyc_document(file)
        
        # Upload to system
        document = kyc.upload_document(phone_number, doc_type, file_data, filename)
        
        # Simulate OCR extraction (in production, use real OCR service)
        extracted_data = {
            'number': 'ID1234567890',
            'name': 'John Doe',
            'dob': '1990-01-15',
            'expiry': '2030-01-15'
        }
        
        # Verify document
        kyc.verify_document(phone_number, document.doc_id, extracted_data, 'system')
        
        return jsonify({
            'success': True,
            'document_id': document.doc_id,
            'extracted_data': extracted_data,
            'status': 'verified'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## Part 4: Transaction Processing

### Step 4.1: Transaction Middleware

```python
# middleware/transaction_middleware.py
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime

def log_transaction(f):
    """Middleware to log all transactions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.transaction_start_time = datetime.now()
        g.transaction_id = f"TXN_{int(datetime.now().timestamp() * 1000)}"
        
        result = f(*args, **kwargs)
        
        g.transaction_duration = (datetime.now() - g.transaction_start_time).total_seconds()
        
        return result
    return decorated_function

def require_kyc(f):
    """Require KYC verification for endpoint"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        phone_number = request.headers.get('X-Phone-Number')
        
        profile = kyc.get_profile(phone_number)
        if not profile or not profile.is_verified():
            return jsonify({'error': 'KYC verification required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function
```

### Step 4.2: Transfer Processing

```python
# services/transfer_service.py
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TransferService:
    
    def process_phone_transfer(self, from_phone, to_phone, amount, user_id):
        """Process phone-to-phone transfer"""
        
        try:
            # Validate
            if amount <= 0:
                raise ValueError("Invalid amount")
            
            if amount > cards.transaction_limit:
                raise ValueError(f"Exceeds limit: R{cards.transaction_limit}")
            
            # Get cards
            from_card = cards.get_card(from_phone)
            to_card = cards.get_card(to_phone)
            
            if not from_card or not to_card:
                raise ValueError("Card not found")
            
            # Check balance
            fee = cards.transfer_fee_phone
            if from_card.balance_rands < amount + fee:
                raise ValueError("Insufficient balance")
            
            # Execute transfer
            transfer = cards.transfer_phone_to_phone(from_phone, to_phone, amount)
            
            # Record transaction in analytics
            from batuma_gprs_weather.analytics.transaction_analytics import Transaction
            txn = Transaction(
                f"TXN_{transfer.transfer_id}",
                "transfer",
                f"USER_{user_id}",
                f"ROUTE_{from_phone}",
                amount
            )
            analytics.add_transaction(txn)
            
            logger.info(f"Transfer completed: {from_phone} → {to_phone}: R{amount}")
            
            return transfer
        
        except Exception as e:
            logger.error(f"Transfer error: {str(e)}")
            raise
    
    def process_bank_transfer(self, from_phone, to_bank, to_account, amount, user_id):
        """Process bank transfer"""
        
        try:
            # Validate
            if amount <= 0 or amount > cards.max_transfer_amount:
                raise ValueError("Invalid amount")
            
            # Get card
            from_card = cards.get_card(from_phone)
            if not from_card:
                raise ValueError("Card not found")
            
            # Check KYC
            kyc_profile = kyc.get_profile(from_phone)
            if not kyc_profile or not kyc_profile.is_verified():
                raise ValueError("KYC verification required")
            
            # Check biometric for high amounts
            security_level, required_auth = biometric.require_authentication_for_transaction(amount)
            if required_auth:
                # Need biometric + passcode for R500+
                logger.info(f"Biometric required for R{amount} transfer")
            
            # Initiate transfer
            transfer = banking.initiate_transfer(
                from_phone, to_account, "001001", to_bank, amount,
                f"Transfer to {to_bank}"
            )
            
            logger.info(f"Bank transfer initiated: R{amount} to {to_bank}")
            
            return transfer
        
        except Exception as e:
            logger.error(f"Bank transfer error: {str(e)}")
            raise

transfer_service = TransferService()
```

---

## Part 5: Monitoring & Logging

### Step 5.1: Setup Logging

```python
# utils/logger.py
import logging
import logging.handlers
from datetime import datetime

def setup_logging(app, log_level='INFO'):
    """Setup application logging"""
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/tap_trip_financial.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        handlers=[file_handler, console_handler]
    )
```

### Step 5.2: Metrics Collection

```python
# services/metrics_service.py
from datetime import datetime, timedelta
from collections import defaultdict

class MetricsService:
    
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def record_transaction(self, transaction_type, amount, status, duration):
        """Record transaction metric"""
        self.metrics['transactions'].append({
            'type': transaction_type,
            'amount': amount,
            'status': status,
            'duration': duration,
            'timestamp': datetime.now()
        })
    
    def get_hourly_metrics(self):
        """Get hourly metrics"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        recent_txns = [
            t for t in self.metrics['transactions']
            if t['timestamp'] > hour_ago
        ]
        
        return {
            'total_transactions': len(recent_txns),
            'successful': sum(1 for t in recent_txns if t['status'] == 'completed'),
            'failed': sum(1 for t in recent_txns if t['status'] == 'failed'),
            'total_amount': sum(t['amount'] for t in recent_txns),
            'avg_duration': sum(t['duration'] for t in recent_txns) / len(recent_txns) if recent_txns else 0
        }
    
    def get_system_health(self):
        """Get system health status"""
        hourly = self.get_hourly_metrics()
        success_rate = (hourly['successful'] / hourly['total_transactions'] * 100) if hourly['total_transactions'] > 0 else 100
        
        return {
            'status': 'healthy' if success_rate > 95 else 'warning',
            'success_rate': success_rate,
            'transactions_per_hour': hourly['total_transactions'],
            'avg_response_time': hourly['avg_duration']
        }

metrics_service = MetricsService()
```

---

## Part 6: Testing

### Step 6.1: Unit Tests

```python
# tests/test_virtual_card.py
import unittest
from batuma_gprs_weather.payment.virtual_card_system import VirtualCardSystem

class TestVirtualCard(unittest.TestCase):
    
    def setUp(self):
        self.system = VirtualCardSystem()
    
    def test_create_card(self):
        card = self.system.create_card("27123456789", "John Doe")
        self.assertIsNotNone(card)
        self.assertEqual(card.phone_number, "27123456789")
        self.assertIsNotNone(card.account_number)
    
    def test_load_money(self):
        card = self.system.create_card("27123456789", "John Doe")
        success = self.system.load_money_from_bank("27123456789", 500, "FNB", "1234567890")
        self.assertTrue(success)
        self.assertEqual(card.get_balance(), 500)
    
    def test_phone_transfer(self):
        card1 = self.system.create_card("27123456789", "John")
        card2 = self.system.create_card("27987654321", "Jane")
        
        self.system.load_money_from_bank("27123456789", 500, "FNB", "1234567890")
        
        transfer = self.system.transfer_phone_to_phone("27123456789", "27987654321", 100)
        
        self.assertIsNotNone(transfer)
        self.assertEqual(transfer.status, "completed")
```

### Step 6.2: Integration Tests

```python
# tests/test_integration.py
import unittest
from app import app, cards, kyc, biometric

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
    
    def test_complete_onboarding_flow(self):
        # Step 1: Create card
        response = self.app.post('/api/financial/cards/create', 
            json={
                'phone_number': '27123456789',
                'customer_name': 'Test User'
            }
        )
        self.assertEqual(response.status_code, 201)
        
        # Step 2: Load money
        response = self.app.post('/api/financial/cards/27123456789/load-money',
            json={'amount': 500, 'source': 'bank'}
        )
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Verify balance
        response = self.app.get('/api/financial/cards/27123456789/balance')
        self.assertEqual(response.status_code, 200)
```

---

## Part 7: Deployment Checklist

### Pre-Deployment

- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Code review completed
- [ ] Security audit passed
- [ ] Load testing completed
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Logging configured
- [ ] API documentation updated

### Database

- [ ] Firestore collections created
- [ ] Firestore indexes created
- [ ] Database backup scheduled
- [ ] Database replication configured

### Environment

- [ ] Production .env configured
- [ ] Firebase production credentials set
- [ ] Banking API credentials set
- [ ] Biometric API credentials set
- [ ] SMS/Email service configured

### Security

- [ ] SSL certificates installed
- [ ] API keys rotated
- [ ] Rate limiting configured
- [ ] CORS headers configured
- [ ] Input validation enabled
- [ ] SQL injection protection (N/A - using Firestore)
- [ ] CSRF protection enabled
- [ ] Secret management configured

### Monitoring

- [ ] Error tracking configured (Sentry)
- [ ] Performance monitoring configured
- [ ] Database monitoring configured
- [ ] Alert rules configured
- [ ] Dashboard created

### Deployment

- [ ] Docker image built and tested
- [ ] Kubernetes manifests prepared
- [ ] Load balancer configured
- [ ] Auto-scaling configured
- [ ] Rollback plan in place

---

## Production Deployment

```bash
# Build Docker image
docker build -t tap-trip-financial:v1 .

# Push to registry
docker push registry.example.com/tap-trip-financial:v1

# Deploy to Kubernetes
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify deployment
kubectl get pods -l app=tap-trip-financial
kubectl logs -f deployment/tap-trip-financial
```

---

## Troubleshooting

### Common Issues

**Issue:** Firestore connection fails
```
Solution: Check Firebase credentials, verify project ID, check network connectivity
```

**Issue:** Biometric enrollment failing
```
Solution: Verify samples quality, check Face API credentials, ensure proper lighting
```

**Issue:** Bank transfer pending
```
Solution: Check account verification, verify branch code, check daily limits
```

**Issue:** High latency on analytics queries
```
Solution: Check Firestore indexes, enable caching, optimize query filters
```

---

## Support

For issues or questions:
- Email: support@taptrip.com
- Documentation: PHASE_5_FINANCIAL_SYSTEM.md
- Quick Ref: PHASE_5_QUICK_REFERENCE.md

