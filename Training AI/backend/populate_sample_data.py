#!/usr/bin/env python3
"""
Script to populate sample data for testing the Picup AI platform
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Driver, Client, Order, QueryResolution, AutomatedAction, DashboardReport
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_sample_data():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()

        # Create sample clients
        clients = [
            Client(name="ABC Restaurant", email="orders@abcrestaurant.co.za", phone="0211234567"),
            Client(name="XYZ Store", email="info@xyzstore.co.za", phone="0217654321"),
            Client(name="FastFood Express", email="support@fastfood.co.za", phone="0219876543"),
            Client(name="Grocery Hub", email="orders@groceryhub.co.za", phone="0215551234"),
        ]
        db.session.add_all(clients)
        db.session.commit()

        # Create sample back office users
        backoffice_users = [
            User(username="admin", password_hash=generate_password_hash("admin123"), role="admin", user_type="backoffice"),
            User(username="manager", password_hash=generate_password_hash("manager123"), role="manager", user_type="backoffice"),
        ]
        db.session.add_all(backoffice_users)
        db.session.commit()

        # Create sample frontend users and drivers
        driver_users = [
            User(username="driver1", password_hash=generate_password_hash("driver123"), role="driver", user_type="frontend"),
            User(username="driver2", password_hash=generate_password_hash("driver123"), role="driver", user_type="frontend"),
            User(username="driver3", password_hash=generate_password_hash("driver123"), role="driver", user_type="frontend"),
        ]
        customer_users = [
            User(username="customer1", password_hash=generate_password_hash("customer123"), role="customer", user_type="frontend"),
            User(username="customer2", password_hash=generate_password_hash("customer123"), role="customer", user_type="frontend"),
        ]
        db.session.add_all(driver_users + customer_users)
        db.session.commit()

        # Create driver profiles
        drivers = [
            Driver(user_id=driver_users[0].id, name="John Driver", phone="0821234567", earnings=1500.50),
            Driver(user_id=driver_users[1].id, name="Jane Driver", phone="0827654321", earnings=1200.75),
            Driver(user_id=driver_users[2].id, name="Mike Driver", phone="0829998888", earnings=980.25),
        ]
        db.session.add_all(drivers)
        db.session.commit()

        # Create sample orders for the last 30 days
        order_statuses = ['pending', 'assigned', 'delivered', 'cancelled', 'no_driver']
        stores = [
            "ABC Restaurant - Cape Town", "XYZ Store - Johannesburg", "FastFood Express - Durban",
            "Grocery Hub - Pretoria", "ABC Restaurant - Johannesburg", "XYZ Store - Cape Town"
        ]

        orders = []
        for i in range(200):  # Create 200 sample orders
            days_ago = random.randint(0, 30)
            order_date = datetime.now() - timedelta(days=days_ago)

            order = Order(
                id=f"PICUP{random.randint(1000, 9999)}",
                client_id=random.choice(clients).id,
                store_name=random.choice(stores),
                date=order_date,
                status=random.choice(order_statuses),
                amount=round(random.uniform(50, 500), 2),
                escalated=random.choice([True, False]) if random.random() < 0.1 else False  # 10% escalated
            )

            # Assign driver to some orders
            if order.status in ['assigned', 'delivered'] and random.random() < 0.8:
                order.driver_id = random.choice(drivers).id

            orders.append(order)

        db.session.add_all(orders)
        db.session.commit()

        # Create sample query resolutions
        query_types = ['driver_assignment', 'payment_issue', 'delivery_delay', 'order_cancellation', 'vehicle_issue', 'wrong_order', 'general_inquiry']
        priorities = ['low', 'medium', 'high', 'critical']

        resolutions = []
        for i in range(150):  # Create 150 sample query resolutions
            days_ago = random.randint(0, 30)
            created_at = datetime.now() - timedelta(days=days_ago)

            resolution = QueryResolution(
                query_type=random.choice(query_types),
                order_id=random.choice(orders).id if random.random() < 0.7 else None,
                driver_id=random.choice(drivers).id if random.random() < 0.5 else None,
                client_id=random.choice(clients).id if random.random() < 0.5 else None,
                status='resolved',
                priority=random.choice(priorities),
                resolution_type='auto' if random.random() < 0.85 else 'manual',  # 85% auto-resolved
                ai_confidence=round(random.uniform(0.7, 0.95), 2),
                resolution_details=f"Auto-resolved {random.choice(query_types)} query",
                created_at=created_at,
                resolved_at=created_at + timedelta(minutes=random.randint(1, 30)),
                response_time=random.randint(1, 300),
                user_satisfaction=random.randint(3, 5)
            )
            resolutions.append(resolution)

        db.session.add_all(resolutions)
        db.session.commit()

        # Create sample automated actions
        action_types = ['assign_driver', 'cancel_order', 'refund', 'escalate_order']

        actions = []
        for i in range(80):  # Create 80 sample automated actions
            days_ago = random.randint(0, 30)
            created_at = datetime.now() - timedelta(days=days_ago)

            action = AutomatedAction(
                action_type=random.choice(action_types),
                order_id=random.choice(orders).id,
                driver_id=random.choice(drivers).id if random.random() < 0.6 else None,
                client_id=random.choice(clients).id if random.random() < 0.4 else None,
                parameters={'auto_generated': True, 'reason': f'Sample {random.choice(action_types)}'},
                status='executed',
                executed_at=created_at + timedelta(minutes=random.randint(1, 15)),
                result=f'Successfully executed {random.choice(action_types)}'
            )
            actions.append(action)

        db.session.add_all(actions)
        db.session.commit()

        print("Sample data created successfully!")
        print("\nLogin Credentials:")
        print("Back Office Admin: admin / admin123")
        print("Back Office Manager: manager / manager123")
        print("Driver 1: driver1 / driver123")
        print("Driver 2: driver2 / driver123")
        print("Driver 3: driver3 / driver123")
        print("Customer 1: customer1 / customer123")
        print("Customer 2: customer2 / customer123")
        print("\nSample Data Summary:")
        print(f"- {len(clients)} clients created")
        print(f"- {len(drivers)} drivers created")
        print(f"- {len(orders)} orders created (last 30 days)")
        print(f"- {len(resolutions)} query resolutions created")
        print(f"- {len(actions)} automated actions created")
        print("\nAutomated System Features:")
        print("- 85% of queries are auto-resolved")
        print("- Daily reports generated automatically at 23:59")
        print("- Real-time driver assignment for 'no_driver' orders")
        print("- Instant payment processing and ledger updates")
        print("- Automated order cancellation and refunds")
        print("- Comprehensive reporting dashboard")

if __name__ == "__main__":
    create_sample_data()