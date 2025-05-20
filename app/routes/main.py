from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, make_response, send_file
from flask_login import login_required, current_user
import csv
import io
import requests
from app import db
from app.models.models import Call, Assistant

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
    
    return render_template('dashboard.html', 
                          pending_calls=pending_calls, 
                          attending_calls=attending_calls,
                          completed_calls=completed_calls)

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
        
    if request.method == 'POST':
        code = request.form.get('code')
        assistant = Assistant.query.filter_by(code=code, active=True).first()
        
        if assistant:
            resp = make_response(redirect(url_for('main.dashboard')))
            resp.set_cookie('asistente', code, max_age=12*60*60)  # Cookie válida para 12 horas
            flash(f'Enrolamiento exitoso. Bienvenido {assistant.name}')
            return resp
        else:
            flash('Código de asistente inválido')
    
    return render_template('enroll.html')

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
                                call_map={}))
            resp.delete_cookie('asistente')
            return resp
    
    # Obtener las llamadas activas para la visualización
    active_calls = Call.query.filter(Call.status.in_(['pending', 'attending'])).all()
    
    # Crear un mapa de llamadas activas para facilitar la búsqueda
    call_map = {}
    for call in active_calls:
        key = f"{call.room}_{call.bed}"
        call_map[key] = call
    
    return render_template('simulacion.html', 
                          is_assistant=is_assistant,
                          assistant=assistant,
                          call_map=call_map) 