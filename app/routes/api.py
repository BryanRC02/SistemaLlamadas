from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
import requests
from app import db
from app.models.models import Call, Assistant
from sqlalchemy import or_

api_bp = Blueprint('api', __name__)

# Función para enviar la notificación via Pushover
def send_pushover_notification(message, title, url=None, url_title=None):
    """Enviar notificación via Pushover API"""
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

# Función para controlar el rele (encender/apagar la luz)
def control_relay(room, bed, action):
    """Controla el rele de una habitación y cama específica
    
    Args:
        room: Número de habitación
        bed: Identificador de la cama (a o b)
        action: Acción a realizar (on o off)
        
    Returns:
        Boolean indicando si la operación fue exitosa
    """
    room_number = int(room)
    relay_base_ip = current_app.config['RELAY_BASE_IP']
    relay_endpoint = current_app.config['RELAY_ENDPOINT']
    
    # Construir la dirección IP del relé para la habitación
    relay_ip = f"{relay_base_ip}.{room_number}"
    
    # Construir la URL para controlar el relé
    # Formato: http://172.17.2.104/relay/0?turn=on
    url = f"http://{relay_ip}{relay_endpoint}?turn={action}"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Control relay: {url}, Response: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error al controlar el relé: {e}")
        return False

@api_bp.route('/llamada/<room>/<bed>', methods=['GET'])
def call(room, bed):
    """Manejar la llamada de un paciente
    
    URL ejemplo: http://172.17.0.10/llamada/104/b
    """
    # Verificar si ya existe una llamada pendiente o en atención para esta habitación y cama
    existing_call = Call.query.filter_by(room=room, bed=bed).filter(
        or_(Call.status == 'pending', Call.status == 'attending')
    ).first()
    
    if existing_call:
        return jsonify({'status': 'info', 'message': 'Ya existe una llamada para esta habitación y cama'})
    
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
    """Manejar la presencia de un asistente en una habitación y cama específica
    
    URL ejemplo: http://172.17.0.10/presencia/104/b
    """
    # Encontrar la llamada activa para esta habitación y cama
    call = Call.query.filter_by(room=room, bed=bed, status='attending').first()
    
    if call:
        # Actualizar el registro de la llamada indicando que el asistente está presente y la fecha y hora de la presencia
        call.presence_time = datetime.utcnow()
        call.status = 'completed'
        db.session.commit()
        
        # Apagar el piloto luminoso
        success = control_relay(room, bed, 'off')
        
        return jsonify({
            'status': 'success', 
            'message': 'Presencia registrada', 
            'relay_success': success
        })
    else:
        return jsonify({'status': 'error', 'message': 'No se encontró una llamada activa para esta habitación y cama'})

@api_bp.route('/atender/<int:call_id>', methods=['GET'])
def attend_call(call_id):
    """Manejar la atención de una llamada por parte de un asistente"""
    # Obtener el código del asistente desde la cookie
    assistant_code = request.cookies.get('asistente')
    
    # Si no hay cookie de asistente, redirigir a la página de enrolamiento con el ID de la llamada
    if not assistant_code:
        return jsonify({
            'status': 'redirect', 
            'redirect_url': f'/enroll?call_id={call_id}',
            'message': 'Se requiere enrolar el dispositivo'
        })
    
    # Encontrar el asistente en la base de datos
    assistant = Assistant.query.filter_by(code=assistant_code, active=True).first()
    if not assistant:
        return jsonify({
            'status': 'redirect', 
            'redirect_url': f'/enroll?call_id={call_id}',
            'message': 'Código de asistente inválido o inactivo'
        })
    
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
    
    # Encender el piloto luminoso de la habitación correspondiente
    success = control_relay(call.room, call.bed, 'on')
    
    return jsonify({
        'status': 'success', 
        'message': 'Asistencia confirmada',
        'relay_success': success
    })

# Rutas para simular el comportamiento de los pulsadores y relés (solo para pruebas)
@api_bp.route('/test/simulate/llamada/<room>/<bed>', methods=['GET'])
def simulate_call(room, bed):
    """Simula la pulsación del botón de llamada"""
    server_ip = current_app.config['SERVER_IP']
    url = f"http://{server_ip}/llamada/{room}/{bed}"
    
    try:
        response = requests.get(url, timeout=5)
        return jsonify({
            'status': 'success',
            'simulation': 'call_button',
            'response': response.json()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@api_bp.route('/test/simulate/presencia/<room>/<bed>', methods=['GET'])
def simulate_presence(room, bed):
    """Simula la pulsación del botón de presencia"""
    server_ip = current_app.config['SERVER_IP']
    url = f"http://{server_ip}/presencia/{room}/{bed}"
    
    try:
        response = requests.get(url, timeout=5)
        return jsonify({
            'status': 'success',
            'simulation': 'presence_button',
            'response': response.json()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@api_bp.route('/test/relay/<room>/<action>', methods=['GET'])
def test_relay(room, action):
    """Endpoint de prueba para controlar directamente un relé"""
    if action not in ['on', 'off']:
        return jsonify({'status': 'error', 'message': 'Acción inválida. Use "on" u "off"'})
    
    try:
        success = control_relay(room, 'a', action)  # Por defecto usamos la cama 'a' para pruebas
        return jsonify({
            'status': 'success' if success else 'error',
            'message': f'Relé de habitación {room} {"encendido" if action == "on" else "apagado"}',
            'success': success
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}) 