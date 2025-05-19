from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
import requests
from app import db
from app.models.models import Call, Assistant

api_bp = Blueprint('api', __name__)

# Function to send Pushover notification
def send_pushover_notification(message, title, url=None, url_title=None):
    """Send notification via Pushover API"""
    payload = {
        'token': current_app.config['PUSHOVER_API_TOKEN'],
        'user': current_app.config['PUSHOVER_USER_KEY'],
        'message': message,
        'title': title,
        'priority': 2,  # Emergency priority
        'retry': 30,    # Retry every 30 seconds
        'expire': 180,  # Expire after 3 minutes
        'sound': 'siren' # Use siren sound
    }
    
    if url:
        payload['url'] = url
    if url_title:
        payload['url_title'] = url_title
    
    response = requests.post('https://api.pushover.net/1/messages.json', data=payload)
    return response.json()

# Function to control the relay (turn on/off the light)
def control_relay(room, bed, action):
    """Control the relay for a specific room and bed"""
    # In a real system, we would have a mapping of room/bed to relay IP
    # For this demo, we'll use a convention: 172.17.2.{room_number}
    room_number = int(room)
    relay_ip = f"172.17.2.{room_number}"
    
    # Construct the URL to control the relay
    url = f"http://{relay_ip}/relay/0?turn={action}"
    
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Error controlling relay: {e}")
        return False

@api_bp.route('/llamada/<room>/<bed>', methods=['GET'])
def call(room, bed):
    """Handle call from a patient"""
    # Create a new call record
    new_call = Call(room=room, bed=bed, status='pending')
    db.session.add(new_call)
    db.session.commit()
    
    # Send notification to assistants
    base_url = request.host_url.rstrip('/')
    call_url = f"{base_url}/atender/{new_call.id}"
    
    message = f"Solicitud de asistencia en habitación {room} y cama {bed}"
    title = "Nueva solicitud de asistencia"
    url_title = "Atender solicitud de asistencia"
    
    send_pushover_notification(message, title, call_url, url_title)
    
    return jsonify({'status': 'success', 'message': 'Call registered'})

@api_bp.route('/presencia/<room>/<bed>', methods=['GET'])
def presence(room, bed):
    """Handle presence button press in a room"""
    # Find the active call for this room and bed
    call = Call.query.filter_by(room=room, bed=bed, status='attending').first()
    
    if call:
        # Update the call record
        call.presence_time = datetime.utcnow()
        call.status = 'completed'
        db.session.commit()
        
        # Turn off the light
        control_relay(room, bed, 'off')
        
        return jsonify({'status': 'success', 'message': 'Presence registered'})
    else:
        return jsonify({'status': 'error', 'message': 'No active call found for this room and bed'})

@api_bp.route('/atender/<int:call_id>', methods=['GET'])
def attend_call(call_id):
    """Handle assistant attending a call"""
    # Get assistant code from cookie
    assistant_code = request.cookies.get('asistente')
    if not assistant_code:
        return jsonify({'status': 'error', 'message': 'No assistant enrolled'})
    
    # Find the assistant
    assistant = Assistant.query.filter_by(code=assistant_code, active=True).first()
    if not assistant:
        return jsonify({'status': 'error', 'message': 'Invalid assistant code'})
    
    # Find the call
    call = Call.query.get(call_id)
    if not call:
        return jsonify({'status': 'error', 'message': 'Call not found'})
    
    # Check if call is already being attended
    if call.status == 'attending':
        return jsonify({'status': 'error', 'message': 'Call is already being attended by another assistant'})
    
    # Update the call record
    call.assistant_id = assistant.id
    call.attention_time = datetime.utcnow()
    call.status = 'attending'
    db.session.commit()
    
    # Turn on the light
    control_relay(call.room, call.bed, 'on')
    
    return jsonify({'status': 'success', 'message': 'Call is now being attended'}) 