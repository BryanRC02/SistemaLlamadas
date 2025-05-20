from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import Relay

relays_bp = Blueprint('relays', __name__, url_prefix='/relays')

@relays_bp.before_request
def check_admin():
    """Asegurar que solo los administradores puedan acceder a estas rutas"""
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Acceso restringido. Se requieren privilegios de administrador.')
        return redirect(url_for('main.index'))

@relays_bp.route('/')
@login_required
def index():
    # Obtener todos los relés
    relays = Relay.query.all()
    return render_template('admin/relays.html', relays=relays)

@relays_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_relay():
    if request.method == 'POST':
        room = request.form.get('room')
        bed = request.form.get('bed')
        ip_address = request.form.get('ip_address')
        endpoint = request.form.get('endpoint')
        active = 'active' in request.form
        
        if not room or not bed or not ip_address:
            flash('Todos los campos son obligatorios')
            return redirect(url_for('relays.new_relay'))
        
        # Verificar si ya existe un relé para esa habitación y cama
        existing_relay = Relay.query.filter_by(room=room, bed=bed).first()
        if existing_relay:
            flash('Ya existe un relé configurado para esta habitación y cama')
            return redirect(url_for('relays.new_relay'))
        
        # Crear nuevo relé
        relay = Relay(
            room=room,
            bed=bed,
            ip_address=ip_address,
            endpoint=endpoint if endpoint else '/relay/0',
            active=active
        )
        
        db.session.add(relay)
        db.session.commit()
        
        flash('Relé configurado con éxito')
        return redirect(url_for('relays.index'))
    
    return render_template('admin/new_relay.html')

@relays_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_relay(id):
    relay = Relay.query.get_or_404(id)
    
    if request.method == 'POST':
        room = request.form.get('room')
        bed = request.form.get('bed')
        ip_address = request.form.get('ip_address')
        endpoint = request.form.get('endpoint')
        active = 'active' in request.form
        
        if not room or not bed or not ip_address:
            flash('Todos los campos son obligatorios')
            return redirect(url_for('relays.edit_relay', id=id))
        
        # Verificar si ya existe otro relé para esa habitación y cama (excepto el actual)
        existing_relay = Relay.query.filter(
            Relay.room == room, 
            Relay.bed == bed, 
            Relay.id != id
        ).first()
        
        if existing_relay:
            flash('Ya existe otro relé configurado para esta habitación y cama')
            return redirect(url_for('relays.edit_relay', id=id))
        
        # Actualizar el relé
        relay.room = room
        relay.bed = bed
        relay.ip_address = ip_address
        relay.endpoint = endpoint if endpoint else '/relay/0'
        relay.active = active
        
        db.session.commit()
        
        flash('Relé actualizado con éxito')
        return redirect(url_for('relays.index'))
    
    return render_template('admin/edit_relay.html', relay=relay)

@relays_bp.route('/delete/<int:id>')
@login_required
def delete_relay(id):
    relay = Relay.query.get_or_404(id)
    
    db.session.delete(relay)
    db.session.commit()
    
    flash('Relé eliminado con éxito')
    return redirect(url_for('relays.index')) 