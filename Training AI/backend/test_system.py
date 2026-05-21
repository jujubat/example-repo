#!/usr/bin/env python3
"""
Simple test script to validate the automated system functionality
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work correctly"""
    try:
        from app import create_app, db
        from app.models import User, Driver, Client, Order, QueryResolution, AutomatedAction, DashboardReport
        from app.automated_processor import AutomatedQueryProcessor, ReportingDashboard
        from app.scheduler import start_scheduler
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_app_creation():
    """Test that the Flask app can be created"""
    try:
        from app import create_app
        app = create_app()
        print("✓ Flask app created successfully")
        return True
    except Exception as e:
        print(f"✗ App creation error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    try:
        from app import create_app, db
        app = create_app()
        with app.app_context():
            db.create_all()
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        return False

def test_automated_processor():
    """Test automated processor functionality"""
    try:
        from app.automated_processor import AutomatedQueryProcessor
        # Test with sample query
        result = AutomatedQueryProcessor.process_query(
            chat_id="test_chat",
            message_content="I need a driver for order PICUP1234",
            user_type="customer",
            user_id=1
        )
        print("✓ Automated processor test successful")
        print(f"  Response: {result}")
        return True
    except Exception as e:
        print(f"✗ Automated processor error: {e}")
        return False

def main():
    print("Testing Picup AI Automated System")
    print("=" * 40)

    tests = [
        ("Imports", test_imports),
        ("App Creation", test_app_creation),
        ("Database Connection", test_database_connection),
        ("Automated Processor", test_automated_processor),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        if test_func():
            passed += 1

    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The system is ready.")
        print("\nNext steps:")
        print("1. Run 'python populate_sample_data.py' to create test data")
        print("2. Run 'python app.py' to start the server")
        print("3. Access the dashboard at http://localhost:5000")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()