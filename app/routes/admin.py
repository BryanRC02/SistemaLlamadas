from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
import random
import string
from app import db
from app.models.models import Assistant

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
    assistants = Assistant.query.all()
    return render_template('admin/assistants.html', assistants=assistants)

@admin_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_assistant():
    if request.method == 'POST':
        name = request.form.get('name')
        
        if not name:
            flash('El nombre es obligatorio')
            return redirect(url_for('admin.new_assistant'))
        
        code = generate_assistant_code()
        assistant = Assistant(name=name, code=code, active=True)
        
        db.session.add(assistant)
        db.session.commit()
        
        flash(f'Asistente creado con éxito. Código: {code}')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/new_assistant.html')

@admin_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_assistant(id):
    assistant = Assistant.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        active = 'active' in request.form
        
        if not name:
            flash('El nombre es obligatorio')
            return redirect(url_for('admin.edit_assistant', id=id))
        
        assistant.name = name
        assistant.active = active
        
        db.session.commit()
        
        flash('Asistente actualizado con éxito')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/edit_assistant.html', assistant=assistant)

@admin_bp.route('/delete/<int:id>')
@login_required
def delete_assistant(id):
    assistant = Assistant.query.get_or_404(id)
    
    db.session.delete(assistant)
    db.session.commit()
    
    flash('Asistente eliminado con éxito')
    return redirect(url_for('admin.index')) 