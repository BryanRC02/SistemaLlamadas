from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app import db
from app.models.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Usuario o contraseña incorrectos')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        
        # Comprobar si el usuario es un asistente
        if user.is_assistant:
            return redirect(url_for('main.enroll'))
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        return redirect(next_page)
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    # Verificar si el usuario es asistente para desenrolarlo
    is_assistant = current_user.is_assistant
    
    # Cerrar sesión del usuario
    logout_user()
    
    # Si era asistente, desenrolarlo del dispositivo
    if is_assistant:
        resp = make_response(redirect(url_for('auth.login')))
        # Asegurarse de eliminar la cookie correctamente
        resp.delete_cookie('asistente', path='/')
        flash('Sesión cerrada y desenrolamiento exitoso')
        return resp
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Solo los administradores pueden registrar nuevos usuarios
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Solo los administradores pueden registrar nuevos usuarios')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_assistant = 'is_assistant' in request.form
        
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('El correo electrónico ya está en uso')
            return redirect(url_for('auth.register'))
        
        user = User(username=username, email=email, is_assistant=is_assistant)
        user.set_password(password)
        
        # Hacer el primer usuario un administrador
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        flash('¡Registro exitoso!')
        return redirect(url_for('main.index'))
    
    return render_template('register.html') 