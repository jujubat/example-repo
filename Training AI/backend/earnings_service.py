#!/usr/bin/env python3
"""
Driver Earnings and Trip Information Service
Manages collection, storage, and retrieval of driver earnings and trip data
"""

from app import db
from app.models import DriverEarnings, Driver, TripInfo, AgentKPI, SOPDocument, QueryResolution, User
from picup_scraper import PicupScraper
from datetime import datetime, date, timedelta
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class EarningsService:
    """Service for managing driver earnings data"""

    @staticmethod
    def collect_earnings_data(driver_id: int = None, days_back: int = 30) -> bool:
        """Collect earnings data from Picup backoffice"""
        try:
            scraper = PicupScraper()

            # Calculate date range
            date_to = date.today()
            date_from = date_to - timedelta(days=days_back)

            # Get earnings data
            earnings_data = scraper.get_driver_earnings(
                driver_id=str(driver_id) if driver_id else None,
                date_from=date_from,
                date_to=date_to
            )

            if not earnings_data:
                logger.warning("No earnings data collected from Picup backoffice")
                return False

            # Store earnings data
            stored_count = 0
            for earnings_record in earnings_data:
                if EarningsService._store_earnings_record(earnings_record):
                    stored_count += 1

            logger.info(f"Successfully stored {stored_count} earnings records")
            return stored_count > 0

        except Exception as e:
            logger.error(f"Error collecting earnings data: {e}")
            return False

    @staticmethod
    def collect_trip_data(days_back: int = 30) -> bool:
        """Collect trip information from Picup frontend"""
        try:
            scraper = PicupScraper()

            # Calculate date range
            date_to = date.today()
            date_from = date_to - timedelta(days=days_back)

            # Get trip data
            trip_data = scraper.get_trip_information(
                date_from=date_from,
                date_to=date_to
            )

            if not trip_data:
                logger.warning("No trip data collected from Picup frontend")
                return False

            # Store trip data
            stored_count = 0
            for trip_record in trip_data:
                if EarningsService._store_trip_record(trip_record):
                    stored_count += 1

            logger.info(f"Successfully stored {stored_count} trip records")
            return stored_count > 0

        except Exception as e:
            logger.error(f"Error collecting trip data: {e}")
            return False

    @staticmethod
    def _store_earnings_record(earnings_data: Dict) -> bool:
        """Store a single earnings record in the database"""
        try:
            # Find driver by name or ID
            driver = None

            if earnings_data.get('driver_id'):
                # Try to find by external ID first
                driver = Driver.query.filter_by(external_id=earnings_data['driver_id']).first()

            if not driver and earnings_data.get('driver_name'):
                # Try to find by name
                driver = Driver.query.filter(
                    db.func.lower(Driver.name).contains(earnings_data['driver_name'].lower())
                ).first()

            if not driver:
                logger.warning(f"Could not find driver for earnings record: {earnings_data}")
                return False

            # Parse date
            record_date = date.today()
            if earnings_data.get('date'):
                try:
                    if isinstance(earnings_data['date'], str):
                        record_date = date.fromisoformat(earnings_data['date'])
                    else:
                        record_date = earnings_data['date']
                except (ValueError, TypeError):
                    logger.warning(f"Invalid date format: {earnings_data['date']}")

            # Check if record already exists
            existing_record = DriverEarnings.query.filter_by(
                driver_id=driver.id,
                date=record_date
            ).first()

            if existing_record:
                # Update existing record
                existing_record.total_earnings = earnings_data.get('total_earnings', 0)
                existing_record.trips_completed = earnings_data.get('trips_completed', 0)
                existing_record.cash_collected = earnings_data.get('cash_collected', 0)
                existing_record.tips_received = earnings_data.get('tips_received', 0)
                existing_record.bonuses = earnings_data.get('bonuses', 0)
                existing_record.deductions = earnings_data.get('deductions', 0)
                existing_record.net_earnings = earnings_data.get('net_earnings', 0)
                existing_record.source = earnings_data.get('source', 'picup_backoffice')
                existing_record.last_updated = datetime.utcnow()
            else:
                # Create new record
                earnings_record = DriverEarnings(
                    driver_id=driver.id,
                    date=record_date,
                    total_earnings=earnings_data.get('total_earnings', 0),
                    trips_completed=earnings_data.get('trips_completed', 0),
                    cash_collected=earnings_data.get('cash_collected', 0),
                    tips_received=earnings_data.get('tips_received', 0),
                    bonuses=earnings_data.get('bonuses', 0),
                    deductions=earnings_data.get('deductions', 0),
                    net_earnings=earnings_data.get('net_earnings', 0),
                    source=earnings_data.get('source', 'picup_backoffice')
                )
                db.session.add(earnings_record)

            db.session.commit()
            return True

        except Exception as e:
            logger.error(f"Error storing earnings record: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def _store_trip_record(trip_data: Dict) -> bool:
        """Store a single trip record in the database"""
        try:
            # Check if trip already exists
            existing_trip = TripInfo.query.filter_by(trip_id=trip_data['trip_id']).first()

            if existing_trip:
                # Update existing record
                existing_trip.order_id = trip_data.get('order_id')
                existing_trip.driver_name = trip_data.get('driver_name')
                existing_trip.client_name = trip_data.get('client_name')
                existing_trip.store_name = trip_data.get('store_name')
                existing_trip.pickup_address = trip_data.get('pickup_address')
                existing_trip.delivery_address = trip_data.get('delivery_address')
                existing_trip.status = trip_data.get('status')
                existing_trip.amount = trip_data.get('amount', 0)
                existing_trip.distance = trip_data.get('distance', 0)
                existing_trip.duration = trip_data.get('duration')
                existing_trip.scheduled_time = EarningsService._parse_datetime(trip_data.get('scheduled_time'))
                existing_trip.pickup_time = EarningsService._parse_datetime(trip_data.get('pickup_time'))
                existing_trip.delivery_time = EarningsService._parse_datetime(trip_data.get('delivery_time'))
                existing_trip.created_at = EarningsService._parse_datetime(trip_data.get('created_at'))
                existing_trip.source = trip_data.get('source', 'picup_frontend')
                existing_trip.last_updated = datetime.utcnow()
            else:
                # Create new record
                trip_record = TripInfo(
                    trip_id=trip_data['trip_id'],
                    order_id=trip_data.get('order_id'),
                    driver_name=trip_data.get('driver_name'),
                    client_name=trip_data.get('client_name'),
                    store_name=trip_data.get('store_name'),
                    pickup_address=trip_data.get('pickup_address'),
                    delivery_address=trip_data.get('delivery_address'),
                    status=trip_data.get('status'),
                    amount=trip_data.get('amount', 0),
                    distance=trip_data.get('distance', 0),
                    duration=trip_data.get('duration'),
                    scheduled_time=EarningsService._parse_datetime(trip_data.get('scheduled_time')),
                    pickup_time=EarningsService._parse_datetime(trip_data.get('pickup_time')),
                    delivery_time=EarningsService._parse_datetime(trip_data.get('delivery_time')),
                    created_at=EarningsService._parse_datetime(trip_data.get('created_at')),
                    source=trip_data.get('source', 'picup_frontend')
                )
                db.session.add(trip_record)

            db.session.commit()
            return True

        except Exception as e:
            logger.error(f"Error storing trip record: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def _parse_datetime(datetime_str: str) -> Optional[datetime]:
        """Parse datetime string into datetime object"""
        if not datetime_str:
            return None
        try:
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def get_driver_earnings(driver_id: int, start_date: date = None, end_date: date = None) -> List[Dict]:
        """Get earnings data for a specific driver"""
        try:
            query = DriverEarnings.query.filter_by(driver_id=driver_id)

            if start_date:
                query = query.filter(DriverEarnings.date >= start_date)
            if end_date:
                query = query.filter(DriverEarnings.date <= end_date)

            records = query.order_by(DriverEarnings.date.desc()).all()

            earnings_data = []
            for record in records:
                earnings_data.append({
                    'id': record.id,
                    'date': record.date.isoformat(),
                    'total_earnings': record.total_earnings,
                    'trips_completed': record.trips_completed,
                    'cash_collected': record.cash_collected,
                    'tips_received': record.tips_received,
                    'bonuses': record.bonuses,
                    'deductions': record.deductions,
                    'net_earnings': record.net_earnings,
                    'source': record.source,
                    'last_updated': record.last_updated.isoformat() if record.last_updated else None
                })

            return earnings_data

        except Exception as e:
            logger.error(f"Error getting driver earnings: {e}")
            return []

    @staticmethod
    def get_trip_information(trip_id: str = None, driver_id: int = None, start_date: date = None, end_date: date = None) -> List[Dict]:
        """Get trip information with optional filters"""
        try:
            query = TripInfo.query

            if trip_id:
                query = query.filter_by(trip_id=trip_id)
            if driver_id:
                query = query.filter_by(driver_id=driver_id)
            if start_date:
                query = query.filter(TripInfo.created_at >= start_date)
            if end_date:
                query = query.filter(TripInfo.created_at <= end_date)

            records = query.order_by(TripInfo.created_at.desc()).all()

            trip_data = []
            for record in records:
                trip_data.append({
                    'id': record.id,
                    'trip_id': record.trip_id,
                    'order_id': record.order_id,
                    'driver_name': record.driver_name,
                    'client_name': record.client_name,
                    'store_name': record.store_name,
                    'pickup_address': record.pickup_address,
                    'delivery_address': record.delivery_address,
                    'status': record.status,
                    'amount': record.amount,
                    'distance': record.distance,
                    'duration': record.duration,
                    'scheduled_time': record.scheduled_time.isoformat() if record.scheduled_time else None,
                    'pickup_time': record.pickup_time.isoformat() if record.pickup_time else None,
                    'delivery_time': record.delivery_time.isoformat() if record.delivery_time else None,
                    'created_at': record.created_at.isoformat() if record.created_at else None,
                    'source': record.source
                })

            return trip_data

        except Exception as e:
            logger.error(f"Error getting trip information: {e}")
            return []

    @staticmethod
    def get_driver_earnings_summary(driver_id: int, days: int = 30) -> Dict:
        """Get earnings summary for a driver over the last N days"""
        try:
            start_date = date.today() - timedelta(days=days)

            records = DriverEarnings.query.filter(
                DriverEarnings.driver_id == driver_id,
                DriverEarnings.date >= start_date
            ).all()

            if not records:
                return {
                    'total_earnings': 0,
                    'total_trips': 0,
                    'average_daily': 0,
                    'best_day': None,
                    'period_days': days
                }

            total_earnings = sum(r.total_earnings for r in records)
            total_trips = sum(r.trips_completed for r in records)
            average_daily = total_earnings / days if days > 0 else 0

            best_day = max(records, key=lambda r: r.total_earnings) if records else None
            best_day_data = {
                'date': best_day.date.isoformat(),
                'earnings': best_day.total_earnings,
                'trips': best_day.trips_completed
            } if best_day else None

            return {
                'total_earnings': round(total_earnings, 2),
                'total_trips': total_trips,
                'average_daily': round(average_daily, 2),
                'best_day': best_day_data,
                'period_days': days,
                'records_count': len(records)
            }

        except Exception as e:
            logger.error(f"Error getting earnings summary: {e}")
            return {}

    @staticmethod
    def get_all_drivers_earnings_summary(days: int = 30) -> List[Dict]:
        """Get earnings summary for all drivers"""
        try:
            drivers = Driver.query.all()
            summaries = []

            for driver in drivers:
                summary = EarningsService.get_driver_earnings_summary(driver.id, days)
                if summary:
                    summary['driver_id'] = driver.id
                    summary['driver_name'] = driver.name
                    summary['phone'] = driver.phone
                    summaries.append(summary)

            # Sort by total earnings descending
            summaries.sort(key=lambda x: x.get('total_earnings', 0), reverse=True)
            return summaries

        except Exception as e:
            logger.error(f"Error getting all drivers earnings summary: {e}")
            return []

    @staticmethod
    def sync_earnings_for_all_drivers() -> Dict:
        """Sync earnings data for all drivers from Picup"""
        try:
            drivers = Driver.query.all()
            success_count = 0
            error_count = 0

            for driver in drivers:
                if EarningsService.collect_earnings_data(driver.id):
                    success_count += 1
                else:
                    error_count += 1

            return {
                'total_drivers': len(drivers),
                'successful_syncs': success_count,
                'failed_syncs': error_count,
                'success_rate': round(success_count / len(drivers) * 100, 1) if drivers else 0
            }

        except Exception as e:
            logger.error(f"Error syncing earnings for all drivers: {e}")
            return {
                'error': str(e),
                'total_drivers': 0,
                'successful_syncs': 0,
                'failed_syncs': 0,
                'success_rate': 0
            }

    @staticmethod
    def sync_trip_data_for_all() -> Dict:
        """Sync trip data from Picup frontend"""
        try:
            success = EarningsService.collect_trip_data()
            return {
                'success': success,
                'message': 'Trip data sync completed' if success else 'Trip data sync failed'
            }
        except Exception as e:
            logger.error(f"Error syncing trip data: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def calculate_driver_earnings_from_trips(driver_id: int, target_date: date = None) -> Dict:
        """Calculate earnings from trip data when Picup data is unavailable"""
        try:
            from app.models import Trip

            if not target_date:
                target_date = date.today()

            # Get trips for the date
            trips = Trip.query.filter(
                Trip.driver_id == driver_id,
                db.func.date(Trip.date) == target_date,
                Trip.status == 'paid'
            ).all()

            total_earnings = sum(trip.amount for trip in trips)
            trips_count = len(trips)

            # Store calculated earnings
            earnings_record = DriverEarnings(
                driver_id=driver_id,
                date=target_date,
                total_earnings=total_earnings,
                trips_completed=trips_count,
                net_earnings=total_earnings,
                source='calculated'
            )

            # Check if record exists
            existing = DriverEarnings.query.filter_by(
                driver_id=driver_id,
                date=target_date
            ).first()

            if existing:
                existing.total_earnings = total_earnings
                existing.trips_completed = trips_count
                existing.net_earnings = total_earnings
                existing.source = 'calculated'
                existing.last_updated = datetime.utcnow()
            else:
                db.session.add(earnings_record)

            db.session.commit()

            return {
                'driver_id': driver_id,
                'date': target_date.isoformat(),
                'total_earnings': total_earnings,
                'trips_completed': trips_count,
                'source': 'calculated'
            }

        except Exception as e:
            logger.error(f"Error calculating driver earnings: {e}")
            return {}


class KPIService:
    """Service for managing agent KPI tracking"""

    @staticmethod
    def calculate_agent_kpis(target_date: date = None) -> bool:
        """Calculate KPIs for all agents for a specific date"""
        try:
            if not target_date:
                target_date = date.today()

            # Get all back office users
            agents = User.query.filter_by(user_type='backoffice').all()

            for agent in agents:
                KPIService._calculate_single_agent_kpi(agent.id, target_date)

            logger.info(f"Calculated KPIs for {len(agents)} agents for {target_date}")
            return True

        except Exception as e:
            logger.error(f"Error calculating agent KPIs: {e}")
            return False

    @staticmethod
    def _calculate_single_agent_kpi(user_id: int, target_date: date) -> bool:
        """Calculate KPIs for a single agent"""
        try:
            # Get query resolutions for the agent on the target date
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = datetime.combine(target_date, datetime.max.time())

            resolutions = QueryResolution.query.filter(
                QueryResolution.created_at >= start_datetime,
                QueryResolution.created_at <= end_datetime
            ).all()

            # For now, we'll assign queries to agents based on some logic
            # In a real system, you'd track which agent handled each query
            agent_resolutions = [r for r in resolutions if r.id % len(User.query.filter_by(user_type='backoffice').all()) == (user_id % len(User.query.filter_by(user_type='backoffice').all()))]

            if not agent_resolutions:
                # Create empty KPI record
                kpi_record = AgentKPI(
                    user_id=user_id,
                    date=target_date,
                    total_queries_assigned=0,
                    queries_responded=0,
                    queries_resolved=0
                )
                db.session.add(kpi_record)
                db.session.commit()
                return True

            # Calculate metrics
            total_assigned = len(agent_resolutions)
            responded = len([r for r in agent_resolutions if r.status in ['resolved', 'escalated']])
            resolved = len([r for r in agent_resolutions if r.status == 'resolved'])

            # Calculate response times
            response_times = []
            resolution_times = []
            feedback_times = []

            for resolution in agent_resolutions:
                if resolution.resolved_at and resolution.created_at:
                    response_time = (resolution.resolved_at - resolution.created_at).total_seconds() / 60
                    response_times.append(response_time)
                    resolution_times.append(response_time)

                if resolution.user_satisfaction:
                    feedback_times.append(60)  # Placeholder - would need actual feedback timing

            # Calculate averages
            first_response_avg = sum(response_times) / len(response_times) if response_times else None
            resolution_time_avg = sum(resolution_times) / len(resolution_times) if resolution_times else None
            feedback_time_avg = sum(feedback_times) / len(feedback_times) if feedback_times else None

            satisfaction_scores = [r.user_satisfaction for r in agent_resolutions if r.user_satisfaction]
            satisfaction_avg = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else None

            escalation_rate = len([r for r in agent_resolutions if r.status == 'escalated']) / total_assigned * 100 if total_assigned > 0 else 0

            # Check if KPI record exists
            existing_kpi = AgentKPI.query.filter_by(user_id=user_id, date=target_date).first()

            if existing_kpi:
                existing_kpi.total_queries_assigned = total_assigned
                existing_kpi.queries_responded = responded
                existing_kpi.queries_resolved = resolved
                existing_kpi.first_response_time_avg = first_response_avg
                existing_kpi.resolution_time_avg = resolution_time_avg
                existing_kpi.feedback_time_avg = feedback_time_avg
                existing_kpi.customer_satisfaction_avg = satisfaction_avg
                existing_kpi.escalation_rate = escalation_rate
                existing_kpi.updated_at = datetime.utcnow()
            else:
                kpi_record = AgentKPI(
                    user_id=user_id,
                    date=target_date,
                    total_queries_assigned=total_assigned,
                    queries_responded=responded,
                    queries_resolved=resolved,
                    first_response_time_avg=first_response_avg,
                    resolution_time_avg=resolution_time_avg,
                    feedback_time_avg=feedback_time_avg,
                    customer_satisfaction_avg=satisfaction_avg,
                    escalation_rate=escalation_rate
                )
                db.session.add(kpi_record)

            db.session.commit()
            return True

        except Exception as e:
            logger.error(f"Error calculating KPI for agent {user_id}: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def get_agent_kpi(user_id: int, start_date: date = None, end_date: date = None) -> List[Dict]:
        """Get KPI data for a specific agent"""
        try:
            query = AgentKPI.query.filter_by(user_id=user_id)

            if start_date:
                query = query.filter(AgentKPI.date >= start_date)
            if end_date:
                query = query.filter(AgentKPI.date <= end_date)

            records = query.order_by(AgentKPI.date.desc()).all()

            kpi_data = []
            for record in records:
                kpi_data.append({
                    'id': record.id,
                    'date': record.date.isoformat(),
                    'total_queries_assigned': record.total_queries_assigned,
                    'queries_responded': record.queries_responded,
                    'queries_resolved': record.queries_resolved,
                    'first_response_time_avg': record.first_response_time_avg,
                    'resolution_time_avg': record.resolution_time_avg,
                    'feedback_time_avg': record.feedback_time_avg,
                    'customer_satisfaction_avg': record.customer_satisfaction_avg,
                    'escalation_rate': record.escalation_rate
                })

            return kpi_data

        except Exception as e:
            logger.error(f"Error getting agent KPI: {e}")
            return []

    @staticmethod
    def get_all_agents_kpi_ranking(start_date: date = None, end_date: date = None) -> List[Dict]:
        """Get KPI ranking for all agents from best to worst"""
        try:
            if not start_date:
                start_date = date.today() - timedelta(days=30)
            if not end_date:
                end_date = date.today()

            # Get all agents
            agents = User.query.filter_by(user_type='backoffice').all()

            agent_rankings = []

            for agent in agents:
                kpi_records = AgentKPI.query.filter(
                    AgentKPI.user_id == agent.id,
                    AgentKPI.date >= start_date,
                    AgentKPI.date <= end_date
                ).all()

                if kpi_records:
                    # Calculate aggregate metrics
                    total_assigned = sum(r.total_queries_assigned for r in kpi_records)
                    total_resolved = sum(r.queries_resolved for r in kpi_records)
                    avg_response_time = sum(r.first_response_time_avg or 0 for r in kpi_records) / len(kpi_records)
                    avg_satisfaction = sum(r.customer_satisfaction_avg or 0 for r in kpi_records) / len(kpi_records)
                    avg_escalation = sum(r.escalation_rate or 0 for r in kpi_records) / len(kpi_records)

                    resolution_rate = (total_resolved / total_assigned * 100) if total_assigned > 0 else 0

                    agent_rankings.append({
                        'agent_id': agent.id,
                        'agent_name': f"{agent.username} ({agent.role})",
                        'total_queries_assigned': total_assigned,
                        'total_queries_resolved': total_resolved,
                        'resolution_rate': round(resolution_rate, 1),
                        'avg_first_response_time': round(avg_response_time, 1) if avg_response_time > 0 else None,
                        'avg_customer_satisfaction': round(avg_satisfaction, 1) if avg_satisfaction > 0 else None,
                        'avg_escalation_rate': round(avg_escalation, 1),
                        'period_days': (end_date - start_date).days + 1
                    })

            # Sort by resolution rate (best to worst)
            agent_rankings.sort(key=lambda x: x['resolution_rate'], reverse=True)

            return agent_rankings

        except Exception as e:
            logger.error(f"Error getting agent KPI ranking: {e}")
            return []


class SOPService:
    """Service for managing Standard Operating Procedures"""

    @staticmethod
    def get_sop_for_query(query_type: str) -> Optional[Dict]:
        """Get the relevant SOP for a query type"""
        try:
            sop = SOPDocument.query.filter_by(
                category=query_type,
                is_active=True
            ).order_by(SOPDocument.version.desc()).first()

            if sop:
                return {
                    'id': sop.id,
                    'title': sop.title,
                    'content': sop.content,
                    'category': sop.category,
                    'version': sop.version,
                    'updated_at': sop.updated_at.isoformat() if sop.updated_at else None
                }

            return None

        except Exception as e:
            logger.error(f"Error getting SOP for query type {query_type}: {e}")
            return None

    @staticmethod
    def create_sop(title: str, content: str, category: str, created_by: int) -> bool:
        """Create a new SOP document"""
        try:
            sop = SOPDocument(
                title=title,
                content=content,
                category=category,
                created_by=created_by
            )
            db.session.add(sop)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating SOP: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def update_sop(sop_id: int, title: str = None, content: str = None, category: str = None) -> bool:
        """Update an existing SOP"""
        try:
            sop = SOPDocument.query.get(sop_id)
            if not sop:
                return False

            if title:
                sop.title = title
            if content:
                sop.content = content
            if category:
                sop.category = category

            sop.updated_at = datetime.utcnow()
            db.session.commit()
            return True

        except Exception as e:
            logger.error(f"Error updating SOP: {e}")
            db.session.rollback()
            return False


def update_earnings_scheduler():
    """Scheduled task to update earnings data"""
    logger.info("Starting scheduled earnings update")
    result = EarningsService.sync_earnings_for_all_drivers()
    logger.info(f"Earnings sync completed: {result}")


def update_trip_data_scheduler():
    """Scheduled task to update trip data"""
    logger.info("Starting scheduled trip data update")
    result = EarningsService.sync_trip_data_for_all()
    logger.info(f"Trip data sync completed: {result}")


def update_kpi_scheduler():
    """Scheduled task to calculate agent KPIs"""
    logger.info("Starting scheduled KPI calculation")
    success = KPIService.calculate_agent_kpis()
    logger.info(f"KPI calculation completed: {'Success' if success else 'Failed'}")


if __name__ == "__main__":
    # Test the services
    print("Testing Earnings and KPI Services...")

    # Test collecting earnings
    print("Collecting earnings data...")
    success = EarningsService.collect_earnings_data()
    print(f"Earnings collection result: {success}")

    # Test collecting trip data
    print("Collecting trip data...")
    success = EarningsService.collect_trip_data()
    print(f"Trip data collection result: {success}")

    # Test KPI calculation
    print("Calculating agent KPIs...")
    success = KPIService.calculate_agent_kpis()
    print(f"KPI calculation result: {success}")

    # Test getting agent rankings
    print("Getting agent KPI rankings...")
    rankings = KPIService.get_all_agents_kpi_ranking()
    print(f"Found {len(rankings)} agents in ranking")

    if rankings:
        print("Top 3 agents:")
        for i, agent in enumerate(rankings[:3], 1):
            print(f"{i}. {agent['agent_name']}: {agent['resolution_rate']}% resolution rate")