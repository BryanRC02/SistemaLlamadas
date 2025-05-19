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
        'priority': 2,
        'retry': 30,
        'expire': 180,
        'sound': 'siren'
    }
    
    if url:
        payload['url'] = url
    if url_title:
        payload['url_title'] = url_title
    
    response = requests.post('https://api.pushover.net/1/messages.json', data=payload)
    return response.json()

# Function to control the relay (turn on/off the light)
def control_relay(room, bed, action):
    """Controla el rele de una habitación y cama específica"""

    room_number = int(room)
    relay_ip = f"172.17.2.{room_number}"
    
    # Construir la URL para controlar el rele
    url = f"http://{relay_ip}/relay/0?turn={action}"
    
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Error controlling relay: {e}")
        return False

@api_bp.route('/llamada/<room>/<bed>', methods=['GET'])
def call(room, bed):
    """Manejar la llamada de un paciente"""
    # Crear un nuevo registro de llamada
    new_call = Call(room=room, bed=bed, status='pending')
    db.session.add(new_call)
    db.session.commit()
    
    # Enviar notificación a los asistentes
    base_url = request.host_url.rstrip('/')
    call_url = f"{base_url}/atender/{new_call.id}"
    
    message = f"Solicitud de asistencia en habitación {room} y cama {bed}"
    title = "Nueva solicitud de asistencia"
    url_title = "Atender solicitud de asistencia"
    
    send_pushover_notification(message, title, call_url, url_title)
    
    return jsonify({'status': 'success', 'message': 'Call registered'})

@api_bp.route('/presencia/<room>/<bed>', methods=['GET'])
def presence(room, bed):
    """Manejar la presencia de un asistente en una habitación y cama específica"""
    # Encontrar la llamada activa para esta habitación y cama
    call = Call.query.filter_by(room=room, bed=bed, status='attending').first()
    
    if call:
        # Actualizar el registro de la llamada indicando que el asistente está presente y la fecha y hora de la presencia
        call.presence_time = datetime.utcnow()
        call.status = 'completed'
        db.session.commit()
        
        # Apagar el piloto
        control_relay(room, bed, 'off')
        
        return jsonify({'status': 'success', 'message': 'Presencia registrada'})
    else:
        return jsonify({'status': 'error', 'message': 'No se encontró una llamada activa para esta habitación y cama'})

@api_bp.route('/atender/<int:call_id>', methods=['GET'])
def attend_call(call_id):
    """Manejar la atención de una llamada por parte de un asistente"""
    # Obtener el código del asistente desde la cookie
    assistant_code = request.cookies.get('asistente')
    if not assistant_code:
        return jsonify({'status': 'error', 'message': 'No se ha enrolado un asistente'})
    
    # Encontrar el asistente en la base de datos
    assistant = Assistant.query.filter_by(code=assistant_code, active=True).first()
    if not assistant:
        return jsonify({'status': 'error', 'message': 'Código de asistente inválido'})
    
    # Encontrar la llamada en la base de datos
    call = Call.query.get(call_id)
    if not call:
        return jsonify({'status': 'error', 'message': 'Llamada no encontrada'})
    
    # Comprobar si la llamada ya está siendo atendida por otro asistente
    if call.status == 'attending':
        return jsonify({'status': 'error', 'message': 'La llamada ya está siendo atendida por otro asistente'})
    
    # Actualizar el registro de la llamada indicando que el asistente está atendiendo la llamada y la fecha y hora de la atención
    call.assistant_id = assistant.id
    call.attention_time = datetime.utcnow()
    call.status = 'attending'
    db.session.commit()
    
    # Encender el piloto
    control_relay(call.room, call.bed, 'on')
    
    return jsonify({'status': 'success', 'message': 'La llamada está siendo atendida'}) 