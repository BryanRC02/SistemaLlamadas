from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, redirect, url_for, flash, render_template, send_from_directory
import requests
from app import db
from app.models.models import Call, Assistant, Relay
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
        'sound': 'persistent'
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
    try:
        # Buscar el relé correspondiente en la base de datos
        relay = Relay.get_for_room_bed(room, bed.upper())
        
        if relay:
            # Si encontramos el relé, usamos su IP y endpoint
            relay_url = f"http://{relay.ip_address}{relay.endpoint}?turn={action}"
            current_app.logger.info(f"Controlando relé para habitación {room}, cama {bed} en {relay_url}")
            
            # En modo de desarrollo/simulación, usamos la ruta local
            if current_app.config.get('SIMULATION_MODE', True):
                base_url = request.host_url.rstrip('/')
                relay_url = f"{base_url}/relay/{relay.id}?turn={action}"
            
            response = requests.get(relay_url, timeout=5)
            current_app.logger.info(f"Control relay: {relay_url}, Response: {response.status_code}")
            return response.status_code == 200
        else:
            # Si no encontramos el relé, usamos la ruta por defecto
            current_app.logger.warning(f"No se encontró relé para habitación {room}, cama {bed}. Usando ruta por defecto.")
            base_url = request.host_url.rstrip('/')
            relay_url = f"{base_url}/relay/0?turn={action}"
            
            response = requests.get(relay_url, timeout=5)
            current_app.logger.info(f"Control relay (default): {relay_url}, Response: {response.status_code}")
            return response.status_code == 200
    except Exception as e:
        current_app.logger.error(f"Error al controlar el relé: {e}")
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
    # Verificar si la solicitud es desde un navegador (Accept header contiene text/html)
    is_browser_request = 'text/html' in request.headers.get('Accept', '')
    
    # Encontrar la llamada activa para esta habitación y cama
    call = Call.query.filter_by(room=room, bed=bed, status='attending').first()
    
    if call:
        # Actualizar el registro de la llamada indicando que el asistente está presente y la fecha y hora de la presencia
        call.presence_time = datetime.utcnow()
        call.status = 'completed'
        db.session.commit()
        
        # Apagar el piloto luminoso
        try:
            # Construir la URL para apagar el piloto
            success = control_relay(room, bed, 'off')
            current_app.logger.info(f"Registrando presencia: Habitación {room}, Cama {bed}, Piloto: {'apagado' if success else 'error'}")
        except Exception as e:
            current_app.logger.error(f"Error al apagar el piloto: {e}")
            success = False
        
        # Si es una solicitud desde un navegador, redirigir a la página principal
        if is_browser_request:
            flash('Presencia registrada exitosamente. La llamada ha sido completada.')
            return redirect(url_for('main.dashboard'))
        
        return jsonify({
            'status': 'success', 
            'message': 'Presencia registrada', 
            'relay_success': success
        })
    else:
        if is_browser_request:
            flash('No se encontró una llamada activa para esta habitación y cama')
            return redirect(url_for('main.dashboard'))
            
        return jsonify({'status': 'error', 'message': 'No se encontró una llamada activa para esta habitación y cama'})

@api_bp.route('/atender/<int:call_id>', methods=['GET'])
def attend_call(call_id):
    """Manejar la atención de una llamada por parte de un asistente"""
    # Obtener el código del asistente desde la cookie
    assistant_code = request.cookies.get('asistente')
    
    # Verificar si la solicitud es desde un navegador (Accept header contiene text/html)
    is_browser_request = 'text/html' in request.headers.get('Accept', '')
    
    # Si es una solicitud desde un navegador, redirigir a la ruta principal
    if is_browser_request:
        return redirect(url_for('main.atender_llamada', call_id=call_id))
    
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
    if call.status == 'attending' and call.assistant_id != assistant.id:
        return jsonify({'status': 'error', 'message': 'La llamada ya está siendo atendida por otro asistente'})
    
    # Actualizar el registro de la llamada indicando que el asistente está atendiendo la llamada y la fecha y hora de la atención
    call.assistant_id = assistant.id
    call.attention_time = datetime.utcnow()
    call.status = 'attending'
    db.session.commit()
    
    # Encender el piloto luminoso de la habitación correspondiente
    success = control_relay(call.room, call.bed, 'on')
    current_app.logger.info(f"Atendiendo llamada {call_id}: Habitación {call.room}, Cama {call.bed}, Piloto: {'encendido' if success else 'error'}")
    
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
        success = control_relay(room, 'a', action)
        
        if is_browser_request():
            return redirect(url_for('api.relay_control', relay_id=0, turn=action))
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message': f'Relé de habitación {room} {"encendido" if action == "on" else "apagado"}',
            'success': success
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Función auxiliar para verificar si la solicitud es desde un navegador
def is_browser_request():
    """Verifica si la solicitud es desde un navegador"""
    return 'text/html' in request.headers.get('Accept', '')

@api_bp.route('/relay/<int:relay_id>', methods=['GET'])
def relay_control(relay_id):
    """Endpoint para controlar el estado del relé y mostrar la imagen correspondiente
    
    URL ejemplo: http://172.17.0.10/relay/0?turn=on
    """
    action = request.args.get('turn', 'off')
    
    # Determinar qué imagen mostrar basado en la acción
    image_file = 'pic_bulbon.gif' if action == 'on' else 'pic_bulboff.gif'
    
    # Si el relay_id no es 0, registrar la acción en la base de datos
    if relay_id > 0:
        try:
            relay = Relay.query.get(relay_id)
            if relay:
                current_app.logger.info(f"Relay {relay_id} (Room: {relay.room}, Bed: {relay.bed}) set to {action}")
        except Exception as e:
            current_app.logger.error(f"Error al buscar el relé {relay_id}: {e}")
    
    # Registrar la acción en los logs para depuración
    current_app.logger.info(f"Relay {relay_id} set to {action}, showing {image_file}")
    
    # Devolver la imagen correspondiente
    return send_from_directory('static', image_file) 