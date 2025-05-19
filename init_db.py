from app import create_app, db
from app.models.models import User, Assistant, Call
from datetime import datetime, timedelta
import random

app = create_app()

def init_db():
    with app.app_context():
        # Crear las tablas
        db.create_all()
        
        # Comprobar si ya tenemos datos
        if User.query.count() > 0:
            print("Database already initialized. Skipping.")
            return
        
        # Crear el usuario administrador
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Crear el usuario regular
        user = User(username='user', email='user@example.com')
        user.set_password('user123')
        db.session.add(user)
        
        # Crear los asistentes
        assistants = [
            Assistant(name='Bryan Ramos', code='ABC123', active=True),
            Assistant(name='María García', code='DEF456', active=True),
            Assistant(name='Carlos López', code='GHI789', active=True),
            Assistant(name='Ana Martínez', code='JKL012', active=True),
            Assistant(name='Pedro Rodríguez', code='MNO345', active=False)
        ]
        
        for assistant in assistants:
            db.session.add(assistant)

        # Crear los usuarios de los asistentes
        assistants_user = [
            User(username='Bryan Ramos', email='bryan@email.com', is_admin=True, is_assistant=True),
            User(username='María García', email='maria@email.com', is_admin=True, is_assistant=True),
            User(username='Carlos López', email='carlos@email.com', is_admin=False, is_assistant=True),
            User(username='Ana Martínez', email='ana@email.com', is_admin=True, is_assistant=True),
            User(username='Pedro Rodríguez', email='pedro@email.com', is_admin=False, is_assistant=True)
        ]

        for assistant_user in assistants_user:
            assistant_user.set_password('PPP2025')
            db.session.add(assistant_user)

        
        # Commit para aplicar los cambios en la base de datos
        db.session.commit()
        
        # Crear algunas llamadas
        now = datetime.utcnow()
        
        # Llamadas pendientes
        for i in range(3):
            room = random.randint(101, 105)
            bed = random.choice(['a', 'b'])
            call = Call(room=str(room), bed=bed, call_time=now - timedelta(minutes=random.randint(5, 30)), status='pending')
            db.session.add(call)
        
        # Llamadas en atención
        for i in range(2):
            room = random.randint(101, 105)
            bed = random.choice(['a', 'b'])
            assistant = random.choice(assistants[:4])
            call_time = now - timedelta(minutes=random.randint(15, 60))
            attention_time = call_time + timedelta(minutes=random.randint(1, 5))
            
            call = Call(
                room=str(room), 
                bed=bed, 
                call_time=call_time,
                attention_time=attention_time,
                assistant_id=assistant.id,
                status='attending'
            )
            db.session.add(call)
        
        # Llamadas completadas
        for i in range(5):
            room = random.randint(101, 105)
            bed = random.choice(['a', 'b'])
            assistant = random.choice(assistants[:4])
            call_time = now - timedelta(minutes=random.randint(60, 1440))  # Últimas 24 horas
            attention_time = call_time + timedelta(minutes=random.randint(1, 5))
            presence_time = attention_time + timedelta(minutes=random.randint(1, 10))
            
            call = Call(
                room=str(room), 
                bed=bed, 
                call_time=call_time,
                attention_time=attention_time,
                presence_time=presence_time,
                assistant_id=assistant.id,
                status='completed'
            )
            db.session.add(call)
        
        # Commit para aplicar los cambios en la base de datos
        db.session.commit()
        
        print("Base de datos inicializada con datos de prueba.")
        print("Usuario administrador: admin / admin123")
        print("Usuario regular: user / user123")
        print("Códigos de los asistentes activos:", ", ".join([a.code for a in assistants if a.active]))

if __name__ == '__main__':
    init_db() 