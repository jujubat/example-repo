from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_jwt_extended import create_access_token

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # customer, driver, backoffice, admin
    user_type = db.Column(db.String(20), nullable=False, default='frontend')  # frontend, backoffice
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    content_type = db.Column(db.String(50))
    version = db.Column(db.String(20), default='1.0')

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    score = db.Column(db.Float)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)
    phase = db.Column(db.String(20))

class QuestionBank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    question = db.Column(db.Text)
    options = db.Column(db.JSON)
    answer = db.Column(db.String(255))
    difficulty = db.Column(db.String(20))

class StudentResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question_bank.id'))
    selected_option = db.Column(db.String(255))
    is_correct = db.Column(db.Boolean)

# New models for livechat and delivery service

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    ip_address = db.Column(db.String(50))
    earnings = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('driver', uselist=False))

class Trip(db.Model):
    id = db.Column(db.String(50), primary_key=True)  # Trip ID
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    store_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, not_paid, cancelled, etc.
    amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    driver = db.relationship('Driver', backref=db.backref('trips', lazy=True))

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=True)
    status = db.Column(db.String(20), default='active')  # active, closed
    language_preference = db.Column(db.String(10), default='en')  # en, af
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('chats', lazy=True))
    driver = db.relationship('Driver', backref=db.backref('chats', lazy=True))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_type = db.Column(db.String(10), nullable=False)  # user, driver, ai
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), default='en')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_url = db.Column(db.String(255))  # For uploaded images
    chat = db.relationship('Chat', backref=db.backref('messages', lazy=True))

class LedgerEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    trip_id = db.Column(db.String(50), db.ForeignKey('trip.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    driver = db.relationship('Driver', backref=db.backref('ledger_entries', lazy=True))
    trip = db.relationship('Trip', backref=db.backref('ledger_entry', uselist=False))

# New models for back office and enhanced order management

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.String(50), primary_key=True)  # Order/escalated order number
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    store_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, assigned, no_driver, delivered, cancelled
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
    escalated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.relationship('Client', backref=db.backref('orders', lazy=True))
    driver = db.relationship('Driver', backref=db.backref('orders', lazy=True))

class QueryResolution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_type = db.Column(db.String(50), nullable=False)  # driver_issue, client_complaint, payment_query, etc.
    order_id = db.Column(db.String(50), db.ForeignKey('order.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    status = db.Column(db.String(20), default='open')  # open, resolved, escalated
    priority = db.Column(db.String(10), default='medium')  # low, medium, high, critical
    resolution_type = db.Column(db.String(20), default='auto')  # auto, manual, escalated
    ai_confidence = db.Column(db.Float)  # AI confidence score
    resolution_details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    response_time = db.Column(db.Integer)  # in seconds
    user_satisfaction = db.Column(db.Integer)  # 1-5 rating
    order = db.relationship('Order', backref=db.backref('query_resolutions', lazy=True))
    driver = db.relationship('Driver', backref=db.backref('query_resolutions', lazy=True))
    client = db.relationship('Client', backref=db.backref('query_resolutions', lazy=True))

class AutomatedAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(50), nullable=False)  # assign_driver, cancel_order, refund, etc.
    order_id = db.Column(db.String(50), db.ForeignKey('order.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    parameters = db.Column(db.JSON)  # Action parameters
    status = db.Column(db.String(20), default='pending')  # pending, executed, failed
    executed_at = db.Column(db.DateTime)
    result = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order = db.relationship('Order', backref=db.backref('automated_actions', lazy=True))
    driver = db.relationship('Driver', backref=db.backref('automated_actions', lazy=True))
    client = db.relationship('Client', backref=db.backref('automated_actions', lazy=True))

class DashboardReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)  # daily_summary, driver_performance, client_satisfaction
    date = db.Column(db.Date, nullable=False)
    data = db.Column(db.JSON)  # Report data
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    period = db.Column(db.String(20), default='daily')  # daily, weekly, monthly

class DriverEarnings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_earnings = db.Column(db.Float, default=0.0)
    trips_completed = db.Column(db.Integer, default=0)
    cash_collected = db.Column(db.Float, default=0.0)
    tips_received = db.Column(db.Float, default=0.0)
    bonuses = db.Column(db.Float, default=0.0)
    deductions = db.Column(db.Float, default=0.0)
    net_earnings = db.Column(db.Float, default=0.0)
    source = db.Column(db.String(50), default='picup_api')  # picup_api, manual, calculated
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    driver = db.relationship('Driver', backref=db.backref('earnings_records', lazy=True))

    __table_args__ = (db.UniqueConstraint('driver_id', 'date', name='unique_driver_date'),)

class TripInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.String(50))
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
    driver_name = db.Column(db.String(100))
    client_name = db.Column(db.String(100))
    store_name = db.Column(db.String(100))
    pickup_address = db.Column(db.Text)
    delivery_address = db.Column(db.Text)
    status = db.Column(db.String(20))
    amount = db.Column(db.Float, default=0.0)
    distance = db.Column(db.Float, default=0.0)
    duration = db.Column(db.String(20))
    scheduled_time = db.Column(db.DateTime)
    pickup_time = db.Column(db.DateTime)
    delivery_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)
    source = db.Column(db.String(50), default='picup_frontend')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    driver = db.relationship('Driver', backref=db.backref('trip_records', lazy=True))

class AgentKPI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_queries_assigned = db.Column(db.Integer, default=0)
    queries_responded = db.Column(db.Integer, default=0)
    queries_resolved = db.Column(db.Integer, default=0)
    first_response_time_avg = db.Column(db.Float)  # in minutes
    resolution_time_avg = db.Column(db.Float)  # in minutes
    feedback_time_avg = db.Column(db.Float)  # in minutes
    customer_satisfaction_avg = db.Column(db.Float)  # 1-5 rating
    escalation_rate = db.Column(db.Float)  # percentage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('kpi_records', lazy=True))

    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='unique_user_date_kpi'),)

class SOPDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # driver_issues, payment_queries, delivery_delays, etc.
    version = db.Column(db.String(20), default='1.0')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('created_sops', lazy=True))
