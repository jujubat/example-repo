from app import db
from ..models import QueryResolution, AutomatedAction, Order, Driver, Client, Message, SOPDocument
from datetime import datetime, timedelta
import re

class AutomatedQueryProcessor:
    """Handles automated query processing and resolution"""

    @staticmethod
    def process_query(chat_id, message_content, user_type, user_id):
        """Main entry point for processing queries automatically"""

        # Extract query information
        query_info = AutomatedQueryProcessor.extract_query_info(message_content)

        # Determine query type and priority
        query_type, priority = AutomatedQueryProcessor.classify_query(message_content, query_info)

        # Create query resolution record
        resolution = QueryResolution(
            query_type=query_type,
            order_id=query_info.get('order_id'),
            driver_id=query_info.get('driver_id') if user_type == 'driver' else None,
            client_id=query_info.get('client_id') if user_type == 'client' else None,
            priority=priority,
            ai_confidence=0.85  # Placeholder confidence score
        )

        db.session.add(resolution)
        db.session.commit()

        # Process based on query type
        response = AutomatedQueryProcessor.handle_query_type(query_type, query_info, user_type, resolution.id)

        # Update resolution with response
        resolution.resolution_details = response
        resolution.status = 'resolved'
        resolution.resolved_at = datetime.utcnow()
        resolution.response_time = 0  # Instant response
        resolution.resolution_type = 'auto'

        db.session.commit()

        return response

    @staticmethod
    def extract_query_info(content):
        """Extract relevant information from query content"""
        info = {}

        # Extract order ID
        order_match = re.search(r'(?:order|escalated)\s*(?:number|#)?\s*([A-Z0-9\-]+)', content, re.IGNORECASE)
        if order_match:
            info['order_id'] = order_match.group(1)

        # Extract store name
        store_match = re.search(r'store\s*(?:name)?\s*[:\-]?\s*([A-Za-z\s]+)', content, re.IGNORECASE)
        if store_match:
            info['store_name'] = store_match.group(1).strip()

        # Extract date
        date_match = re.search(r'(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})', content)
        if date_match:
            info['date'] = date_match.group(1)

        # Extract amounts
        amount_match = re.search(r'R?\s*(\d+(?:\.\d{2})?)', content)
        if amount_match:
            info['amount'] = float(amount_match.group(1))

        return info

    @staticmethod
    def classify_query(content, query_info):
        """Classify query type and determine priority"""
        content_lower = content.lower()

        # High priority issues
        if any(word in content_lower for word in ['emergency', 'urgent', 'broken', 'accident', 'danger']):
            priority = 'critical'
        elif any(word in content_lower for word in ['late', 'delay', 'waiting', 'stuck']):
            priority = 'high'
        elif any(word in content_lower for word in ['payment', 'paid', 'refund', 'money']):
            priority = 'medium'
        else:
            priority = 'low'

        # Determine query type
        if 'no driver' in content_lower or 'assign driver' in content_lower:
            query_type = 'driver_assignment'
        elif 'payment' in content_lower or 'paid' in content_lower:
            query_type = 'payment_issue'
        elif 'late' in content_lower or 'delay' in content_lower:
            query_type = 'delivery_delay'
        elif 'cancel' in content_lower or 'cancelled' in content_lower:
            query_type = 'order_cancellation'
        elif 'broken' in content_lower or 'motorbike' in content_lower:
            query_type = 'vehicle_issue'
        elif 'wrong' in content_lower or 'missing' in content_lower:
            query_type = 'wrong_order'
        else:
            query_type = 'general_inquiry'

        return query_type, priority

    @staticmethod
    def handle_query_type(query_type, query_info, user_type, resolution_id):
        """Handle different types of queries automatically using SOPs"""

        # Get relevant SOP for this query type
        sop = AutomatedQueryProcessor.get_sop_for_query_type(query_type)
        if sop:
            return AutomatedQueryProcessor.apply_sop_response(sop, query_info, user_type)

        # Fallback to original logic if no SOP found
        if query_type == 'driver_assignment':
            return AutomatedQueryProcessor.handle_driver_assignment(query_info, user_type)
        elif query_type == 'payment_issue':
            return AutomatedQueryProcessor.handle_payment_issue(query_info, user_type)
        elif query_type == 'delivery_delay':
            return AutomatedQueryProcessor.handle_delivery_delay(query_info, user_type)
        elif query_type == 'order_cancellation':
            return AutomatedQueryProcessor.handle_order_cancellation(query_info, user_type)
        elif query_type == 'vehicle_issue':
            return AutomatedQueryProcessor.handle_vehicle_issue(query_info, user_type)
        elif query_type == 'wrong_order':
            return AutomatedQueryProcessor.handle_wrong_order(query_info, user_type)
        else:
            return AutomatedQueryProcessor.handle_general_inquiry(query_info, user_type)

    @staticmethod
    def get_sop_for_query_type(query_type):
        """Retrieve the most recent SOP document for a given query type"""
        sop = SOPDocument.query.filter_by(
            category=query_type,
            is_active=True
        ).order_by(SOPDocument.version.desc()).first()

        return sop

    @staticmethod
    def apply_sop_response(sop, query_info, user_type):
        """Apply SOP guidelines to generate automated response"""
        if not sop:
            return "Unable to process query. Please contact support."

        # Get SOP content and extract response template
        sop_content = sop.content

        # Extract automated response section from SOP
        response_template = AutomatedQueryProcessor.extract_response_template(sop_content, query_info)

        if response_template:
            # Fill in template with query information
            response = AutomatedQueryProcessor.fill_template(response_template, query_info, user_type)
        else:
            # Use SOP summary as fallback
            response = sop.summary or "Query processed according to standard operating procedures."

        # Execute any automated actions specified in SOP
        AutomatedQueryProcessor.execute_sop_actions(sop, query_info, user_type)

        return response

    @staticmethod
    def extract_response_template(sop_content, query_info):
        """Extract automated response template from SOP content"""
        # Look for automated response section in SOP
        import re

        # Search for automated response patterns
        response_patterns = [
            r'AUTOMATED RESPONSE[:\s]*(.*?)(?=ACTION|PROCEDURE|END|$)',
            r'RESPONSE TEMPLATE[:\s]*(.*?)(?=ACTION|PROCEDURE|END|$)',
            r'STANDARD RESPONSE[:\s]*(.*?)(?=ACTION|PROCEDURE|END|$)'
        ]

        for pattern in response_patterns:
            match = re.search(pattern, sop_content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()

        return None

    @staticmethod
    def fill_template(template, query_info, user_type):
        """Fill response template with actual query information"""
        response = template

        # Replace placeholders with actual values
        replacements = {
            '{order_id}': query_info.get('order_id', 'N/A'),
            '{store_name}': query_info.get('store_name', 'N/A'),
            '{amount}': f"R{query_info.get('amount', '0.00')}",
            '{date}': query_info.get('date', datetime.utcnow().strftime('%Y-%m-%d')),
            '{user_type}': user_type
        }

        for placeholder, value in replacements.items():
            response = response.replace(placeholder, str(value))

        return response

    @staticmethod
    def execute_sop_actions(sop, query_info, user_type):
        """Execute automated actions specified in SOP"""
        sop_content = sop.content

        # Look for action keywords
        if 'AUTO-ASSIGN' in sop_content.upper():
            AutomatedQueryProcessor.execute_auto_assign(query_info)
        elif 'ESCALATE' in sop_content.upper():
            AutomatedQueryProcessor.execute_escalation(query_info)
        elif 'CANCEL' in sop_content.upper():
            AutomatedQueryProcessor.execute_cancellation(query_info)
        elif 'COMPENSATE' in sop_content.upper():
            AutomatedQueryProcessor.execute_compensation(query_info)

    @staticmethod
    def execute_auto_assign(query_info):
        """Execute automatic driver assignment"""
        order_id = query_info.get('order_id')
        if order_id:
            order = Order.query.get(order_id)
            if order and order.status == 'no_driver':
                available_driver = AutomatedQueryProcessor.find_available_driver(order)
                if available_driver:
                    order.driver_id = available_driver.id
                    order.status = 'assigned'
                    db.session.commit()

                    # Log automated action
                    action = AutomatedAction(
                        action_type='auto_assign_driver',
                        order_id=order_id,
                        driver_id=available_driver.id,
                        parameters={'sop_triggered': True},
                        status='executed',
                        executed_at=datetime.utcnow(),
                        result=f"SOP-triggered assignment to {available_driver.name}"
                    )
                    db.session.add(action)
                    db.session.commit()

    @staticmethod
    def execute_escalation(query_info):
        """Execute query escalation"""
        order_id = query_info.get('order_id')
        if order_id:
            order = Order.query.get(order_id)
            if order:
                order.escalated = True
                db.session.commit()

                # Log escalation
                action = AutomatedAction(
                    action_type='escalate_query',
                    order_id=order_id,
                    parameters={'sop_triggered': True, 'reason': 'SOP escalation'},
                    status='executed',
                    executed_at=datetime.utcnow(),
                    result="Query escalated per SOP"
                )
                db.session.add(action)
                db.session.commit()

    @staticmethod
    def execute_cancellation(query_info):
        """Execute order cancellation"""
        order_id = query_info.get('order_id')
        if order_id:
            order = Order.query.get(order_id)
            if order and order.status in ['pending', 'assigned']:
                order.status = 'cancelled'
                db.session.commit()

                # Log cancellation
                action = AutomatedAction(
                    action_type='cancel_order',
                    order_id=order_id,
                    parameters={'sop_triggered': True},
                    status='executed',
                    executed_at=datetime.utcnow(),
                    result="Order cancelled per SOP"
                )
                db.session.add(action)
                db.session.commit()

    @staticmethod
    def execute_compensation(query_info):
        """Execute compensation action"""
        order_id = query_info.get('order_id')
        if order_id:
            order = Order.query.get(order_id)
            if order:
                # Mark for compensation
                order.escalated = True
                db.session.commit()

                # Log compensation
                action = AutomatedAction(
                    action_type='compensate_order',
                    order_id=order_id,
                    parameters={'sop_triggered': True, 'compensation_type': 'auto'},
                    status='executed',
                    executed_at=datetime.utcnow(),
                    result="Compensation arranged per SOP"
                )
                db.session.add(action)
                db.session.commit()

    @staticmethod
    def handle_driver_assignment(query_info, user_type):
        """Automatically handle driver assignment issues"""
        order_id = query_info.get('order_id')

        if not order_id:
            return "Please provide your order number for driver assignment assistance."

        order = Order.query.get(order_id)
        if not order:
            return f"Order {order_id} not found. Please check your order number."

        if order.status == 'assigned':
            driver = order.driver
            return f"Order {order_id} is already assigned to driver {driver.name} (Phone: {driver.phone}). They should arrive shortly."
        elif order.status == 'no_driver':
            # Auto-assign available driver
            available_driver = AutomatedQueryProcessor.find_available_driver(order)
            if available_driver:
                order.driver_id = available_driver.id
                order.status = 'assigned'
                db.session.commit()

                # Create automated action record
                action = AutomatedAction(
                    action_type='assign_driver',
                    order_id=order_id,
                    driver_id=available_driver.id,
                    parameters={'auto_assigned': True},
                    status='executed',
                    executed_at=datetime.utcnow(),
                    result=f"Auto-assigned driver {available_driver.name}"
                )
                db.session.add(action)
                db.session.commit()

                return f"Driver {available_driver.name} has been automatically assigned to your order {order_id}. They will contact you shortly at {available_driver.phone}."
            else:
                return f"No drivers available for order {order_id} at this time. Your order has been escalated for priority handling."
        else:
            return f"Order {order_id} status: {order.status.upper()}. Please check your order details."

    @staticmethod
    def handle_payment_issue(query_info, user_type):
        """Automatically handle payment-related issues"""
        order_id = query_info.get('order_id')

        if not order_id:
            return "Please provide your order number for payment assistance."

        order = Order.query.get(order_id)
        if not order:
            return f"Order {order_id} not found. Please check your order number."

        if order.status == 'paid':
            return f"Order {order_id} shows as PAID. If you're experiencing issues, please contact customer service."
        elif order.status == 'not_paid':
            # Auto-process payment if amount matches
            amount = query_info.get('amount', order.amount)
            if amount and abs(amount - order.amount) < 0.01:  # Allow small difference
                order.status = 'paid'
                db.session.commit()

                # Add to driver ledger
                from app.routes.livechat import add_to_ledger
                add_to_ledger(order.driver_id, order_id, amount)

                return f"Payment of R{amount} confirmed for order {order_id}. Amount added to driver ledger."
            else:
                return f"Payment amount mismatch for order {order_id}. Expected: R{order.amount}. Please verify and try again."
        else:
            return f"Order {order_id} payment status: {order.status.upper()}."

    @staticmethod
    def handle_delivery_delay(query_info, user_type):
        """Automatically handle delivery delay issues"""
        order_id = query_info.get('order_id')

        if not order_id:
            return "Please provide your order number for delivery status."

        order = Order.query.get(order_id)
        if not order:
            return f"Order {order_id} not found."

        # Check if order is actually delayed
        expected_time = order.date
        current_time = datetime.utcnow()

        if current_time > expected_time + timedelta(minutes=30):
            # Auto-escalate for compensation
            order.escalated = True
            db.session.commit()

            return f"Order {order_id} is delayed. We've escalated this for priority handling and arranged compensation. Driver {order.driver.name} will contact you shortly."
        else:
            return f"Order {order_id} is on time. Expected delivery: {expected_time.strftime('%H:%M')}. Driver: {order.driver.name} ({order.driver.phone})."

    @staticmethod
    def handle_order_cancellation(query_info, user_type):
        """Automatically handle order cancellation requests"""
        order_id = query_info.get('order_id')

        if not order_id:
            return "Please provide your order number for cancellation."

        order = Order.query.get(order_id)
        if not order:
            return f"Order {order_id} not found."

        if order.status in ['pending', 'assigned']:
            order.status = 'cancelled'
            db.session.commit()

            return f"Order {order_id} has been cancelled successfully. Refund will be processed within 24 hours."
        else:
            return f"Order {order_id} cannot be cancelled at this stage (Status: {order.status.upper()}). Please contact customer service."

    @staticmethod
    def handle_vehicle_issue(query_info, user_type):
        """Handle vehicle/motorbike issues"""
        return "Please upload a clear photo of the vehicle issue. Our AI will analyze it and take appropriate action (order cancellation/compensation)."

    @staticmethod
    def handle_wrong_order(query_info, user_type):
        """Handle wrong order deliveries"""
        order_id = query_info.get('order_id')

        if not order_id:
            return "Please provide your order number for wrong order assistance."

        order = Order.query.get(order_id)
        if not order:
            return f"Order {order_id} not found."

        # Auto-escalate wrong orders
        order.escalated = True
        order.status = 'wrong_order'
        db.session.commit()

        return f"Wrong order issue for {order_id} has been escalated. A new order will be prepared immediately. Driver {order.driver.name} will collect the incorrect items."

    @staticmethod
    def handle_general_inquiry(query_info, user_type):
        """Handle general inquiries"""
        return "Thank you for your inquiry. Our AI assistant is here to help. Please provide more details about your specific issue."

    @staticmethod
    def find_available_driver(order):
        """Find an available driver for assignment"""
        # Simple logic: find drivers with least active orders
        drivers = Driver.query.all()
        if not drivers:
            return None

        # Sort by number of active orders
        driver_workload = {}
        for driver in drivers:
            active_orders = len([o for o in driver.orders if o.status == 'assigned'])
            driver_workload[driver.id] = active_orders

        # Return driver with least workload
        min_workload_driver_id = min(driver_workload, key=driver_workload.get)
        return Driver.query.get(min_workload_driver_id)

class ReportingDashboard:
    """Generate automated reports for drivers and clients"""

    @staticmethod
    def generate_daily_report():
        """Generate daily performance report"""
        today = datetime.utcnow().date()

        # Driver performance
        drivers = Driver.query.all()
        driver_stats = []

        for driver in drivers:
            today_orders = [o for o in driver.orders if o.date.date() == today]
            completed_orders = len([o for o in today_orders if o.status == 'delivered'])
            earnings = sum([o.amount for o in today_orders if o.status == 'paid'])

            driver_stats.append({
                'driver_id': driver.id,
                'name': driver.name,
                'completed_orders': completed_orders,
                'earnings': earnings,
                'rating': 4.5  # Placeholder
            })

        # Client satisfaction
        clients = Client.query.all()
        client_stats = []

        for client in clients:
            today_orders = [o for o in client.orders if o.date.date() == today]
            satisfied_orders = len([o for o in today_orders if o.status == 'delivered'])

            client_stats.append({
                'client_id': client.id,
                'name': client.name,
                'total_orders': len(today_orders),
                'satisfied_orders': satisfied_orders
            })

        # Query resolutions
        resolutions = QueryResolution.query.filter(
            db.func.date(QueryResolution.created_at) == today
        ).all()

        resolution_stats = {
            'total_queries': len(resolutions),
            'auto_resolved': len([r for r in resolutions if r.resolution_type == 'auto']),
            'avg_response_time': sum([r.response_time or 0 for r in resolutions]) / len(resolutions) if resolutions else 0
        }

        report_data = {
            'date': today.isoformat(),
            'driver_performance': driver_stats,
            'client_satisfaction': client_stats,
            'query_resolution': resolution_stats
        }

        # Save report
        report = DashboardReport(
            report_type='daily_summary',
            date=today,
            data=report_data,
            period='daily'
        )
        db.session.add(report)
        db.session.commit()

        return report_data

    @staticmethod
    def get_driver_report(driver_id, days=7):
        """Get driver performance report for last N days"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)

        driver = Driver.query.get(driver_id)
        if not driver:
            return None

        orders = [o for o in driver.orders if start_date <= o.date.date() <= end_date]

        report = {
            'driver_name': driver.name,
            'period': f"{start_date} to {end_date}",
            'total_orders': len(orders),
            'completed_orders': len([o for o in orders if o.status == 'delivered']),
            'cancelled_orders': len([o for o in orders if o.status == 'cancelled']),
            'total_earnings': sum([o.amount for o in orders if o.status == 'paid']),
            'avg_rating': 4.5,  # Placeholder
            'daily_breakdown': []
        }

        # Daily breakdown
        for i in range(days):
            date = start_date + timedelta(days=i)
            day_orders = [o for o in orders if o.date.date() == date]
            report['daily_breakdown'].append({
                'date': date.isoformat(),
                'orders': len(day_orders),
                'earnings': sum([o.amount for o in day_orders if o.status == 'paid'])
            })

        return report

    @staticmethod
    def get_client_report(client_id, days=30):
        """Get client satisfaction report"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)

        client = Client.query.get(client_id)
        if not client:
            return None

        orders = [o for o in client.orders if start_date <= o.date.date() <= end_date]

        report = {
            'client_name': client.name,
            'period': f"{start_date} to {end_date}",
            'total_orders': len(orders),
            'delivered_orders': len([o for o in orders if o.status == 'delivered']),
            'cancelled_orders': len([o for o in orders if o.status == 'cancelled']),
            'avg_order_value': sum([o.amount for o in orders]) / len(orders) if orders else 0,
            'satisfaction_rate': len([o for o in orders if o.status == 'delivered']) / len(orders) if orders else 0
        }

        return report