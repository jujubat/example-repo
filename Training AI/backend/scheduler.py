from app import create_app
from app.automated_processor import ReportingDashboard
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

def generate_daily_reports():
    """Scheduled task to generate daily reports"""
    try:
        app = create_app()
        with app.app_context():
            print("Generating daily reports...")
            report = ReportingDashboard.generate_daily_report()
            print(f"Daily report generated for {report['date']}")
            print(f"Processed {report['query_resolution']['total_queries']} queries")
            print(f"Auto-resolution rate: {report['query_resolution']['auto_resolved']/report['query_resolution']['total_queries']*100:.1f}%" if report['query_resolution']['total_queries'] > 0 else "No queries today")
    except Exception as e:
        print(f"Error generating daily reports: {e}")

def start_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()
    # Generate daily reports at 11:59 PM every day
    scheduler.add_job(
        func=generate_daily_reports,
        trigger=CronTrigger(hour=23, minute=59),
        id='daily_reports',
        name='Generate Daily Reports',
        replace_existing=True
    )

    scheduler.start()
    print("Background scheduler started - Daily reports will be generated at 23:59")

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    start_scheduler()
    # Keep the script running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Scheduler stopped")