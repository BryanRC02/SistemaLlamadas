from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_assistant = db.Column(db.Boolean, default=False)
    assistant_code = db.Column(db.String(6), db.ForeignKey('assistant.code'), nullable=True)
    assistant = db.relationship('Assistant', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_active_assistant(self):
        """Verifica si el usuario es un asistente activo"""
        if not self.is_assistant or not self.assistant_code:
            return True  # Si no es asistente, se considera activo
        
        # Buscar el estado del asistente asociado
        assistant = Assistant.query.filter_by(code=self.assistant_code).first()
        if assistant and assistant.active:
            return True
        return False
    
    @property
    def is_active(self):
        """Implementación de la propiedad de Flask-Login que verifica si el usuario está activo"""
        return self.is_active_assistant()
    
    def __repr__(self):
        return f'<User {self.username}>'

class Assistant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    code = db.Column(db.String(6), index=True, unique=True)
    active = db.Column(db.Boolean, default=True)
    calls = db.relationship('Call', backref='attending_assistant', lazy='dynamic')
    
    def __repr__(self):
        return f'<Assistant {self.name}>'

class Call(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.String(10))
    bed = db.Column(db.String(1))
    call_time = db.Column(db.DateTime, default=datetime.utcnow)
    attention_time = db.Column(db.DateTime, nullable=True)
    presence_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, attending, completed
    assistant_id = db.Column(db.Integer, db.ForeignKey('assistant.id'), nullable=True)
    
    def __repr__(self):
        return f'<Call Room:{self.room} Bed:{self.bed} Status:{self.status}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 