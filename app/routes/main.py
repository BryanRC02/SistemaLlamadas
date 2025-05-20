from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, make_response, send_file, abort
from flask_login import login_required, current_user
import csv
import io
import requests
from app import db
from app.models.models import Call, Assistant, Relay
from app.routes.api import control_relay

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return redirect(url_for('main.simulacion'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Obtener las llamadas pendientes, en atención y completadas en las últimas 24 horas
    since = datetime.utcnow() - timedelta(hours=24)
    pending_calls = Call.query.filter(Call.call_time >= since, Call.status == 'pending').all()
    attending_calls = Call.query.filter(Call.call_time >= since, Call.status == 'attending').all()
    completed_calls = Call.query.filter(Call.call_time >= since, Call.status == 'completed').all()
    
    # Verificar si el usuario es un asistente enrolado
    is_assistant = False
    assistant = None
    assistant_code = request.cookies.get('asistente')
    
    if assistant_code and current_user.is_assistant:
        assistant = Assistant.query.filter_by(code=assistant_code, active=True).first()
        if assistant:
            is_assistant = True
    
    return render_template('dashboard.html', 
                          pending_calls=pending_calls, 
                          attending_calls=attending_calls,
                          completed_calls=completed_calls,
                          is_assistant=is_assistant,
                          assistant=assistant)

@main_bp.route('/asistencias')
@login_required
def asistencias():
    # Obtener las llamadas de las últimas 24 horas ordenadas por fecha y hora de llamada
    since = datetime.utcnow() - timedelta(hours=24)
    calls = Call.query.filter(Call.call_time >= since).order_by(Call.call_time.desc()).all()
    
    return render_template('asistencias.html', calls=calls)

@main_bp.route('/enroll', methods=['GET', 'POST'])
@login_required
def enroll():
    # Verificar que el usuario sea un asistente
    if not current_user.is_assistant:
        flash('Solo los asistentes pueden acceder a esta página')
        return redirect(url_for('main.dashboard'))
    
    # Verificar que el asistente esté activo
    if not current_user.is_active_assistant():
        flash('Su cuenta de asistente está desactivada. Por favor, contacte al administrador.')
        return redirect(url_for('main.dashboard'))
    
    # Obtener el ID de la llamada si se proporcionó
    call_id = request.args.get('call_id')
        
    if request.method == 'POST':
        code = request.form.get('code')
        assistant = Assistant.query.filter_by(code=code, active=True).first()
        
        if assistant:
            # Determinar la URL de redirección
            if call_id:
                # Si hay un ID de llamada, redirigir a atender esa llamada después del enrolamiento
                redirect_url = url_for('main.atender_llamada', call_id=call_id)
            else:
                # Caso normal: redirigir al dashboard
                redirect_url = url_for('main.dashboard')
            
            resp = make_response(redirect(redirect_url))
            resp.set_cookie('asistente', code, max_age=12*60*60)  # Cookie válida para 12 horas
            flash(f'Enrolamiento exitoso. Bienvenido {assistant.name}')
            return resp
        else:
            flash('Código de asistente inválido')
    
    return render_template('enroll.html', call_id=call_id)

@main_bp.route('/desenroll')
@login_required
def desenroll():
    # Verificar que el usuario sea un asistente
    if not current_user.is_assistant:
        flash('Solo los asistentes pueden acceder a esta función')
        return redirect(url_for('main.dashboard'))
    
    # Verificar que el asistente esté activo
    if not current_user.is_active_assistant():
        flash('Su cuenta de asistente está desactivada. Por favor, contacte al administrador.')
        return redirect(url_for('main.dashboard'))
        
    resp = make_response(redirect(url_for('main.dashboard')))
    resp.delete_cookie('asistente', path='/')
    flash('Desenrolamiento exitoso')
    return resp

@main_bp.route('/export_csv')
@login_required
def export_csv():
    # Obtener las llamadas de las últimas 24 horas
    since = datetime.utcnow() - timedelta(hours=24)
    calls = Call.query.filter(Call.call_time >= since).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escribir la cabecera
    writer.writerow(['ID', 'Habitación', 'Cama', 'Hora de Llamada', 'Hora de Atención', 
                    'Hora de Presencia', 'Estado', 'Asistente'])
    
    # Escribir los datos
    for call in calls:
        assistant_name = call.attending_assistant.name if call.attending_assistant else ''
        writer.writerow([
            call.id, 
            call.room, 
            call.bed, 
            call.call_time, 
            call.attention_time, 
            call.presence_time, 
            call.status, 
            assistant_name
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename=f'llamadas_{datetime.utcnow().strftime("%Y%m%d")}.csv'
    )

@main_bp.route('/simulacion')
def simulacion():
    # Obtener el código del asistente desde la cookie si está disponible
    assistant_code = request.cookies.get('asistente')
    is_assistant = False
    assistant = None
    
    if assistant_code:
        # Verificar que el código existe y corresponde a un asistente activo
        assistant = Assistant.query.filter_by(code=assistant_code, active=True).first()
        if assistant:
            is_assistant = True
        else:
            # Si el código no es válido, eliminamos la cookie
            resp = make_response(render_template('simulacion.html', 
                                is_assistant=False,
                                assistant=None,
                                call_map={},
                                relay_map={}))
            resp.delete_cookie('asistente')
            return resp
    
    # Obtener las llamadas activas para la visualización
    active_calls = Call.query.filter(Call.status.in_(['pending', 'attending'])).all()
    
    # Crear un mapa de llamadas activas para facilitar la búsqueda
    call_map = {}
    for call in active_calls:
        key = f"{call.room}_{call.bed}"
        call_map[key] = call
    
    # Obtener todos los relés activos
    relays = Relay.query.filter_by(active=True).all()
    
    # Crear un mapa de relés para facilitar la búsqueda
    relay_map = {}
    for relay in relays:
        key = f"{relay.room}_{relay.bed}"
        relay_map[key] = relay
    
    return render_template('simulacion.html', 
                          is_assistant=is_assistant,
                          assistant=assistant,
                          call_map=call_map,
                          relay_map=relay_map)

@main_bp.route('/atender/<int:call_id>')
def atender_llamada(call_id):
    """Maneja la atención de una llamada por un asistente y verifica el enrolamiento del dispositivo"""
    # Verificar si existe la llamada
    call = Call.query.get_or_404(call_id)
    
    # Verificar si la llamada ya está siendo atendida
    if call.status == 'completed':
        flash('Esta llamada ya ha sido completada')
        return redirect(url_for('main.dashboard'))
    
    # Obtener el código del asistente desde la cookie
    assistant_code = request.cookies.get('asistente')
    
    # Si no hay cookie de asistente o no está autenticado, redirigir a login
    if not assistant_code or not current_user.is_authenticated:
        # Guardar el ID de la llamada para redirigir después del login/enrolamiento
        next_url = url_for('main.atender_llamada', call_id=call_id)
        return redirect(url_for('auth.login', next=next_url))
    
    # Verificar si el asistente existe y está activo
    assistant = Assistant.query.filter_by(code=assistant_code, active=True).first()
    if not assistant:
        # Si el código no es válido, redirigir a la página de enrolamiento
        flash('Dispositivo no enrolado o código inválido')
        return redirect(url_for('main.enroll', call_id=call_id))
    
    # Si la llamada ya está siendo atendida por otro asistente, mostrar mensaje
    if call.status == 'attending' and call.assistant_id != assistant.id:
        flash('Esta llamada ya está siendo atendida por otro asistente')
        return redirect(url_for('main.dashboard'))
    
    # Si la llamada no está siendo atendida o está siendo atendida por este asistente
    if call.status == 'pending' or (call.status == 'attending' and call.assistant_id == assistant.id):
        # Si está pendiente, actualizar el estado a "attending"
        if call.status == 'pending':
            call.assistant_id = assistant.id
            call.attention_time = datetime.utcnow()
            call.status = 'attending'
            db.session.commit()
            
            # Encender el piloto luminoso de la habitación correspondiente
            try:
                success = control_relay(call.room, call.bed, 'on')
                current_app.logger.info(f"Atendiendo llamada {call_id}: Habitación {call.room}, Cama {call.bed}, Piloto: {'encendido' if success else 'error'}")
            except Exception as e:
                current_app.logger.error(f"Error al encender piloto: {e}")
        
        # Mostrar la pantalla de confirmación
        return render_template('atencion_confirmada.html', call=call, assistant=assistant)
    
    # Caso no contemplado, redirigir al dashboard
    return redirect(url_for('main.dashboard')) 