from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
import random
import string
from app import db
from app.models.models import Assistant, User

admin_bp = Blueprint('admin', __name__, url_prefix='/asistentes')

def generate_assistant_code():
    """Generar un código aleatorio de 6 caracteres para los asistentes"""
    chars = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(6))
        if not Assistant.query.filter_by(code=code).first():
            return code

@admin_bp.before_request
def check_admin():
    """Asegurar que solo los administradores puedan acceder a estas rutas"""
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Acceso restringido. Se requieren privilegios de administrador.')
        return redirect(url_for('main.index'))

@admin_bp.route('/')
@login_required
def index():
    # Obtener todos los asistentes con sus usuarios asociados
    assistants = Assistant.query.all()
    
    # Crear diccionarios para almacenar la información del usuario asociado a cada asistente
    assistant_users = {}
    assistant_is_admin = {}
    assistant_emails = {}
    
    # Buscar los usuarios asociados a cada asistente
    for assistant in assistants:
        user = User.query.filter_by(assistant_code=assistant.code).first()
        if user:
            assistant_users[assistant.id] = user.username
            assistant_is_admin[assistant.id] = user.is_admin
            assistant_emails[assistant.id] = user.email
        else:
            assistant_users[assistant.id] = "No tiene usuario"
            assistant_is_admin[assistant.id] = False
            assistant_emails[assistant.id] = "N/A"
    
    return render_template(
        'admin/assistants.html', 
        assistants=assistants, 
        assistant_users=assistant_users,
        assistant_is_admin=assistant_is_admin,
        assistant_emails=assistant_emails
    )

@admin_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_assistant():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form
        
        if not name:
            flash('El nombre es obligatorio')
            return redirect(url_for('admin.new_assistant'))
        
        # Generar código único para el asistente
        code = generate_assistant_code()
        
        # Crear el asistente en la tabla de asistentes
        assistant = Assistant(name=name, code=code, active=True)
        db.session.add(assistant)
        
        # Crear un usuario asociado para el asistente
        username = name
        user_email = email if email else f"{name.strip().lower()}@sistemallamadas.local"
        
        # Verificar si el nombre de usuario ya existe
        if User.query.filter_by(username=username).first():
            flash('Error: Ya existe un usuario con ese nombre de usuario')
            return redirect(url_for('admin.new_assistant'))
        
        # Verificar si el correo electrónico ya está en uso
        if User.query.filter_by(email=user_email).first():
            flash('Error: Ya existe un usuario con ese correo electrónico')
            return redirect(url_for('admin.new_assistant'))
        
        # Crear el usuario
        user = User(
            username=username, 
            email=user_email, 
            is_assistant=True, 
            is_admin=is_admin,
            assistant_code=code
        )
        
        # Establecer contraseña (usar PPP2025 por defecto si no se proporciona una)
        if password:
            user.set_password(password)
        else:
            user.set_password('PPP2025')
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Asistente creado con éxito. Código: {code}. Usuario: {username}')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/new_assistant.html')

@admin_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_assistant(id):
    assistant = Assistant.query.get_or_404(id)
    
    # Buscar el usuario asociado al asistente
    assistant_user = User.query.filter_by(assistant_code=assistant.code).first()
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        active = 'active' in request.form
        is_admin = 'is_admin' in request.form
        password = request.form.get('password')
        
        if not name:
            flash('El nombre es obligatorio')
            return redirect(url_for('admin.edit_assistant', id=id))
        
        assistant.name = name
        assistant.active = active
        
        # Actualizar o crear el usuario asociado
        if assistant_user:
            assistant_user.is_admin = is_admin
            
            # Actualizar el correo electrónico si se proporcionó uno
            if email:
                # Verificar si el correo ya está en uso por otro usuario
                existing_user = User.query.filter(User.email == email, User.id != assistant_user.id).first()
                if existing_user:
                    flash('El correo electrónico ya está en uso por otro usuario')
                    return redirect(url_for('admin.edit_assistant', id=id))
                assistant_user.email = email
            
            # Actualizar la contraseña si se proporcionó una
            if password:
                assistant_user.set_password(password)
                flash('Contraseña actualizada con éxito')
        else:
            # Si no hay usuario asociado, crear uno
            username = assistant.name
            user_email = email if email else f"{username.strip().lower()}@sistemallamadas.local"
            
            # Verificar si el nombre de usuario ya existe
            if not User.query.filter_by(username=username).first():
                # Verificar si el correo ya está en uso
                if User.query.filter_by(email=user_email).first():
                    flash('El correo electrónico ya está en uso por otro usuario')
                    return redirect(url_for('admin.edit_assistant', id=id))
                
                new_user = User(
                    username=username, 
                    email=user_email, 
                    is_assistant=True, 
                    is_admin=is_admin,
                    assistant_code=assistant.code
                )
                
                if password:
                    new_user.set_password(password)
                else:
                    new_user.set_password('PPP2025')
                    
                db.session.add(new_user)
                flash(f'Se ha creado un usuario {username} asociado al asistente')
            else:
                flash('No se pudo crear un usuario asociado (el nombre ya existe)')
        
        db.session.commit()
        
        flash('Asistente actualizado con éxito')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/edit_assistant.html', assistant=assistant, assistant_user=assistant_user)

@admin_bp.route('/delete/<int:id>')
@login_required
def delete_assistant(id):
    assistant = Assistant.query.get_or_404(id)
    
    db.session.delete(assistant)
    db.session.commit()
    
    flash('Asistente eliminado con éxito')
    return redirect(url_for('admin.index')) 