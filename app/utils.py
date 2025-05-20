from flask import current_app
from flask_mail import Message
from app import mail
from threading import Thread
import csv
import io
from datetime import datetime, timedelta
from app.models.models import Call

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body=None, attachments=None):
    """Send an email using Flask-Mail
    
    Args:
        subject: Asunto del correo
        sender: Remitente (si es None, se usa el valor por defecto)
        recipients: Lista de destinatarios
        text_body: Cuerpo del mensaje en texto plano
        html_body: Cuerpo del mensaje en HTML (opcional)
        attachments: Lista de adjuntos en formato (nombre_archivo, tipo_mime, datos)
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    if html_body:
        msg.html = html_body
    
    # Adjuntar archivos si se proporcionan
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    
    # Enviar el correo de forma asíncrona
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    ).start()

def generate_calls_csv(hours=24):
    """Genera un archivo CSV con los registros de llamadas de las últimas X horas"""
    since = datetime.utcnow() - timedelta(hours=hours)
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
    return output.getvalue(), f'llamadas_{datetime.utcnow().strftime("%Y%m%d")}.csv' 