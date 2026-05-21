from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from ..models import User, Driver

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new frontend user (customer/driver)."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'customer')  # customer or driver

    if not username or not password:
        return jsonify(msg='Username and password required'), 400

    if User.query.filter_by(username=username).first():
        return jsonify(msg='Username already exists'), 400

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        role=role,
        user_type='frontend'
    )
    db.session.add(user)
    db.session.commit()

    # If registering as driver, create driver profile
    if role == 'driver':
        driver = Driver(user_id=user.id, name=username)
        db.session.add(driver)
        db.session.commit()

    return jsonify(msg='User registered successfully'), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate frontend user and return a JWT access token."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify(msg='Username and password required'), 400

    user = User.query.filter_by(username=username, user_type='frontend').first()
    if user and check_password_hash(user.password_hash, password):
        token = create_access_token(identity=user.id, additional_claims={'user_type': 'frontend', 'role': user.role})
        return jsonify(access_token=token, role=user.role), 200
    return jsonify(msg='Bad credentials'), 401
