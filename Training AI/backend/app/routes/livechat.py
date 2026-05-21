from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import emit, join_room, leave_room
from app import db, socketio
from ..automated_processor import AutomatedQueryProcessor, ReportingDashboard
from datetime import datetime, timedelta
import openai
import langdetect
from googletrans import Translator
import cv2
import numpy as np
import requests
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

livechat_bp = Blueprint('livechat', __name__)

# Initialize OpenAI and Google Sheets
openai.api_key = os.getenv('OPENAI_API_KEY')
translator = Translator()

# Initialize OpenAI and Google Sheets
openai.api_key = os.getenv('OPENAI_API_KEY')
translator = Translator()

# Google Sheets setup (optional)
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
SPREADSHEET_ID = os.getenv('GOOGLE_SHEET_ID')

service = None
if SERVICE_ACCOUNT_FILE and SPREADSHEET_ID:
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
    except Exception as e:
        print(f"Google Sheets setup failed: {e}")
        service = None

@livechat_bp.route('/start_chat', methods=['POST'])
@jwt_required()
def start_chat():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Create or get driver
    driver = Driver.query.filter_by(user_id=user_id).first()
    if not driver:
        driver = Driver(user_id=user_id, name=user.username)
        db.session.add(driver)
        db.session.commit()
    
    # Create new chat
    chat = Chat(user_id=user_id, driver_id=driver.id)
    db.session.add(chat)
    db.session.commit()
    
    return jsonify({'chat_id': chat.id, 'message': 'Chat started'})

@socketio.on('join_chat')
def handle_join_chat(data):
    chat_id = data['chat_id']
    join_room(str(chat_id))
    emit('status', {'message': 'Joined chat'}, room=str(chat_id))

@socketio.on('send_message')
def handle_send_message(data):
    chat_id = data['chat_id']
    content = data['content']
    sender_type = data['sender_type']  # 'user' or 'driver'
    
    chat = Chat.query.get(chat_id)
    if not chat:
        emit('error', {'message': 'Chat not found'})
        return
    
    # Detect language
    try:
        detected_lang = langdetect.detect(content)
    except:
        detected_lang = 'en'
    
    # Save original message
    message = Message(chat_id=chat_id, sender_type=sender_type, content=content, language=detected_lang)
    db.session.add(message)
    db.session.commit()
    
    # Process message with AI
    ai_response = process_message_with_ai(content, detected_lang, chat)
    
    # Save AI response
    ai_message = Message(chat_id=chat_id, sender_type='ai', content=ai_response, language=detected_lang)
    db.session.add(ai_message)
    db.session.commit()
    
    # Emit messages to room
    emit('new_message', {
        'id': message.id,
        'sender_type': sender_type,
        'content': content,
        'timestamp': message.timestamp.isoformat()
    }, room=str(chat_id))
    
    emit('new_message', {
        'id': ai_message.id,
        'sender_type': 'ai',
        'content': ai_response,
        'timestamp': ai_message.timestamp.isoformat()
    }, room=str(chat_id))

def process_message_with_ai(content, language, chat):
    """Process message using automated query processor"""
    try:
        # Get user type from chat
        user = User.query.get(chat.user_id)
        user_type = 'driver' if user.role == 'driver' else 'client'

        # Use automated processor for instant responses
        response = AutomatedQueryProcessor.process_query(chat.id, content, user_type, chat.user_id)

        # Translate if necessary
        if language != 'en':
            try:
                from googletrans import Translator
                translator = Translator()
                response = translator.translate(response, src='en', dest=language).text
            except:
                pass  # Keep English response if translation fails

        return response

    except Exception as e:
        # Fallback to basic AI processing if automated fails
        return f"I apologize, but I'm experiencing technical difficulties. Please try again or contact customer service. Error: {str(e)}"

def perform_actions(ai_response, chat, original_content):
    # Parse AI response for actions
    response_lower = ai_response.lower()
    
    # Check for order status queries
    if any(keyword in response_lower for keyword in ['order status', 'escalated order', 'assign driver', 'no driver']):
        order_info = extract_order_info(original_content)
        if order_info:
            order_status = check_order_status(order_info)
            if order_status:
                ai_response += f"\n\nOrder Status Update: {order_status}"
    
    if 'add to ledger' in response_lower:
        # Extract trip details and add to ledger
        add_to_ledger(chat.driver_id, 'trip_id_placeholder', 100.0)  # Placeholder values
    
    if 'ask for picture' in response_lower:
        # Logic for picture upload request
        pass
    
    return ai_response

def extract_order_info(content):
    """Extract order information from user message"""
    # Simple regex patterns to extract order details
    import re
    
    order_info = {}
    
    # Look for order/escalated order number
    order_match = re.search(r'(?:order|escalated)\s*(?:number|#)?\s*([A-Z0-9\-]+)', content, re.IGNORECASE)
    if order_match:
        order_info['order_id'] = order_match.group(1)
    
    # Look for store name
    store_match = re.search(r'store\s*(?:name)?\s*[:\-]?\s*([A-Za-z\s]+)', content, re.IGNORECASE)
    if store_match:
        order_info['store_name'] = store_match.group(1).strip()
    
    # Look for date
    date_match = re.search(r'(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})', content)
    if date_match:
        order_info['date'] = date_match.group(1)
    
    return order_info if order_info else None

def check_order_status(order_info):
    """Check order status in the database"""
    order_id = order_info.get('order_id')
    store_name = order_info.get('store_name')
    date_str = order_info.get('date')
    
    if not order_id:
        return None
    
    # Try to find the order
    order = Order.query.get(order_id)
    if not order:
        return f"Order {order_id} not found in the system."
    
    # Verify details match
    mismatches = []
    if store_name and order.store_name.lower() != store_name.lower():
        mismatches.append(f"Store name mismatch: expected {order.store_name}, got {store_name}")
    
    if date_str:
        try:
            query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            order_date = order.date.date()
            if query_date != order_date:
                mismatches.append(f"Date mismatch: expected {order_date}, got {query_date}")
        except ValueError:
            pass
    
    status_response = f"Order {order_id} - Status: {order.status.upper()}"
    if order.driver:
        status_response += f", Assigned to: {order.driver.name}"
    else:
        status_response += ", No driver assigned"
    
    if order.escalated:
        status_response += " (ESCALATED)"
    
    if mismatches:
        status_response += f"\nDetails verification: {'; '.join(mismatches)}"
    else:
        status_response += "\nAll details verified successfully."
    
    return status_response

@livechat_bp.route('/upload_image', methods=['POST'])
@jwt_required()
def upload_image():
    user_id = get_jwt_identity()
    chat_id = request.form.get('chat_id')
    image = request.files.get('image')
    
    if not image:
        return jsonify({'error': 'No image provided'}), 400
    
    # Save image
    image_path = f'uploads/{chat_id}_{datetime.now().timestamp()}.jpg'
    os.makedirs('uploads', exist_ok=True)
    image.save(image_path)
    
    # Analyze image
    analysis_result = analyze_image(image_path, chat_id)
    
    # Save message with image
    message = Message(chat_id=chat_id, sender_type='driver', content='Image uploaded', image_url=image_path)
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'result': analysis_result})

def analyze_image(image_path, chat_id):
    # Load image
    image = cv2.imread(image_path)
    
    # Basic checks (placeholder - implement actual AI vision)
    # Check for broken bike, rain, etc.
    
    # For now, return a placeholder response
    return "Image analyzed. Order removed due to broken bike."

def add_to_ledger(driver_id, trip_id, amount):
    # Add entry to database
    entry = LedgerEntry(driver_id=driver_id, trip_id=trip_id, amount=amount, description='Trip payment')
    db.session.add(entry)
    db.session.commit()
    
    # Update Google Sheet
    update_google_sheet(driver_id, trip_id, amount)

def update_google_sheet(driver_id, trip_id, amount):
    if not service:
        print("Google Sheets not configured, skipping update")
        return
    
    # Append to Google Sheet
    values = [[driver_id, trip_id, amount, datetime.now().isoformat()]]
    body = {'values': values}
    try:
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Sheet1!A:D',
            valueInputOption='RAW',
            body=body
        ).execute()
        print(f"Updated Google Sheet: {result}")
    except Exception as e:
        print(f"Failed to update Google Sheet: {e}")

@livechat_bp.route('/driver_earnings/<int:driver_id>', methods=['GET'])
@jwt_required()
def get_driver_earnings(driver_id):
    driver = Driver.query.get(driver_id)
    if not driver:
        return jsonify({'error': 'Driver not found'}), 404
    
    earnings = db.session.query(db.func.sum(LedgerEntry.amount)).filter_by(driver_id=driver_id).scalar() or 0
    return jsonify({'earnings': earnings})