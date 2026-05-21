from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from ..automated_processor import ReportingDashboard
import re

backoffice_auth_bp = Blueprint('backoffice_auth', __name__)

@backoffice_auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'backoffice')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        role=role,
        user_type='backoffice'
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Back office user registered successfully'})

@backoffice_auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, user_type='backoffice').first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user.id, additional_claims={'user_type': 'backoffice', 'role': user.role})
    return jsonify({'access_token': access_token, 'role': user.role})

@backoffice_auth_bp.route('/dashboard/orders', methods=['GET'])
@jwt_required()
def get_orders():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.user_type != 'backoffice':
        return jsonify({'error': 'Unauthorized'}), 403

    orders = Order.query.all()
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'client_name': order.client.name,
            'store_name': order.store_name,
            'date': order.date.isoformat(),
            'status': order.status,
            'driver_name': order.driver.name if order.driver else None,
            'escalated': order.escalated
        })

    return jsonify({'orders': orders_data})

@backoffice_auth_bp.route('/dashboard/drivers', methods=['GET'])
@jwt_required()
def get_drivers():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.user_type != 'backoffice':
        return jsonify({'error': 'Unauthorized'}), 403

    drivers = Driver.query.all()
    drivers_data = []
    for driver in drivers:
        drivers_data.append({
            'id': driver.id,
            'name': driver.name,
            'phone': driver.phone,
            'earnings': driver.earnings,
            'active_orders': len([o for o in driver.orders if o.status == 'assigned'])
        })

    return jsonify({'drivers': drivers_data})

@backoffice_auth_bp.route('/assign_driver', methods=['POST'])
@jwt_required()
def assign_driver():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.user_type != 'backoffice':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    order_id = data.get('order_id')
    driver_id = data.get('driver_id')

    order = Order.query.get(order_id)
    driver = Driver.query.get(driver_id)

    if not order or not driver:
        return jsonify({'error': 'Order or driver not found'}), 404

    order.driver_id = driver_id
    order.status = 'assigned'
    db.session.commit()

    return jsonify({'message': 'Driver assigned successfully'})

@backoffice_auth_bp.route('/reports/daily', methods=['GET'])
@jwt_required()
def get_daily_report():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.user_type != 'backoffice':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        report = ReportingDashboard.generate_daily_report()
        return jsonify({'report': report})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backoffice_auth_bp.route('/reports/driver/<int:driver_id>', methods=['GET'])
@jwt_required()
def get_driver_report(driver_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.user_type != 'backoffice':
        return jsonify({'error': 'Unauthorized'}), 403

    days = request.args.get('days', 7, type=int)
    report = ReportingDashboard.get_driver_report(driver_id, days)
    if report:
        return jsonify({'report': report})
    return jsonify({'error': 'Driver not found'}), 404

@backoffice_auth_bp.route('/reports/client/<int:client_id>', methods=['GET'])
@jwt_required()
def get_client_report(client_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.user_type != 'backoffice':
        return jsonify({'error': 'Unauthorized'}), 403

    days = request.args.get('days', 30, type=int)
    report = ReportingDashboard.get_client_report(client_id, days)
    if report:
        return jsonify({'report': report})
    return jsonify({'error': 'Client not found'}), 404

@backoffice_auth_bp.route('/analytics/overview', methods=['GET'])
@jwt_required()
def get_analytics_overview():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.user_type != 'backoffice':
        return jsonify({'error': 'Unauthorized'}), 403

    from ..models import QueryResolution, AutomatedAction
    from datetime import datetime, timedelta

    # Get last 30 days stats
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    total_queries = QueryResolution.query.filter(QueryResolution.created_at >= thirty_days_ago).count()
    auto_resolved = QueryResolution.query.filter(
        QueryResolution.created_at >= thirty_days_ago,
        QueryResolution.resolution_type == 'auto'
    ).count()

    total_actions = AutomatedAction.query.filter(AutomatedAction.created_at >= thirty_days_ago).count()
    successful_actions = AutomatedAction.query.filter(
        AutomatedAction.created_at >= thirty_days_ago,
        AutomatedAction.status == 'executed'
    ).count()

    avg_response_time = db.session.query(db.func.avg(QueryResolution.response_time)).filter(
        QueryResolution.created_at >= thirty_days_ago,
        QueryResolution.response_time.isnot(None)
    ).scalar() or 0

    analytics = {
        'total_queries': total_queries,
        'auto_resolution_rate': (auto_resolved / total_queries * 100) if total_queries > 0 else 0,
        'total_automated_actions': total_actions,
        'successful_actions_rate': (successful_actions / total_actions * 100) if total_actions > 0 else 0,
        'avg_response_time_seconds': round(avg_response_time, 2),
        'period': 'last_30_days'
    }

    return jsonify({'analytics': analytics})