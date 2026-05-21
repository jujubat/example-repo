#!/usr/bin/env python3
"""
Simple test script for the Picup AI platform
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    try:
        # Import models directly without triggering app creation
        from app.models import User, Driver, Chat, Message, Trip, LedgerEntry, Order, Client
        from app.routes.livechat import extract_order_info
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_models():
    """Test if models can be instantiated"""
    try:
        from app.models import User, Driver, Order, Client
        # Test model creation (without database)
        user = User(username="test", password_hash="hash", user_type="frontend")
        driver = Driver(user_id=1, name="Test Driver")
        client = Client(name="Test Client", email="test@test.com")
        order = Order(id="TEST001", client_id=1, store_name="Test Store", date="2024-01-01")
        print("✓ Model instantiation successful")
        return True
    except Exception as e:
        print(f"✗ Model instantiation failed: {e}")
        return False

def test_order_checking():
    """Test order checking logic"""
    try:
        from app.routes.livechat import extract_order_info
        # Test order info extraction
        test_content = "My order PICUP001 from ABC Restaurant on 2024-01-01 has no driver assigned"
        order_info = extract_order_info(test_content)
        if order_info and 'order_id' in order_info:
            print("✓ Order info extraction successful")
            return True
        else:
            print("✗ Order info extraction failed")
            return False
    except Exception as e:
        print(f"✗ Order checking test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running Picup AI platform tests...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_models,
        test_order_checking
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Tests passed: {passed}/{len(tests)}")
    if passed == len(tests):
        print("🎉 All tests passed! Picup AI platform is ready.")
        print("\nNext steps:")
        print("1. Install eventlet: pip install eventlet")
        print("2. Run 'python populate_sample_data.py' to create sample data")
        print("3. Run 'python app.py' to start the server")
        print("4. Open http://localhost:5000 in your browser")
        print("\nSample login credentials will be displayed after running populate_sample_data.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    try:
        from app.routes.livechat import extract_order_info, check_order_status
        # Test order info extraction
        test_content = "My order PICUP001 from ABC Restaurant on 2024-01-01 has no driver assigned"
        order_info = extract_order_info(test_content)
        if order_info and 'order_id' in order_info:
            print("✓ Order info extraction successful")
            return True
        else:
            print("✗ Order info extraction failed")
            return False
    except Exception as e:
        print(f"✗ Order checking test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running Picup AI platform tests...")
    print("=" * 50)

    tests = [
        test_imports,
        test_app_creation,
        test_models,
        test_order_checking
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Tests passed: {passed}/{len(tests)}")
    if passed == len(tests):
        print("🎉 All tests passed! Picup AI platform is ready.")
        print("\nNext steps:")
        print("1. Run 'python populate_sample_data.py' to create sample data")
        print("2. Run 'python app.py' to start the server")
        print("3. Open http://localhost:5000 in your browser")
    else:
        print("❌ Some tests failed. Please check the errors above.")