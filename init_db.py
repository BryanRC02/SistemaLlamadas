from app import create_app, db
from app.models.models import User, Assistant, Call, Relay
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
        
        # Commit para guardar los asistentes y obtener sus IDs
        db.session.commit()
        
        # Crear usuarios asociados a los asistentes
        for assistant in assistants:
            username = assistant.name
            email = f"{assistant.name.lower().replace(' ', '')}@sistemallamadas.local"
            assistant_user = User(
                username=username, 
                email=email, 
                is_assistant=True, 
                is_admin=True,
                assistant_code=assistant.code
            )
            assistant_user.set_password('PPP2025')
            db.session.add(assistant_user)
        
        # Commit para aplicar los cambios en la base de datos
        db.session.commit()
        
        # Crear algunas llamadas
        now = datetime.utcnow()
                
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
        
        # Crear los relés para cada habitación y cama
        # Usaremos un formato de IP basado en la habitación: 192.168.{planta}.{habitación}
        relays = []
        
        # Crear relés para las plantas 1-5, habitaciones 1-10, camas A y B
        for floor in range(1, 6):
            for room_num in range(1, 11):
                room_id = floor * 100 + room_num
                
                # Crear relé para la cama A
                relay_a = Relay(
                    room=str(room_id),
                    bed='A',
                    ip_address=f"192.168.{floor}.{room_num}",
                    endpoint='/relay/0',
                    active=True
                )
                relays.append(relay_a)
                
                # Crear relé para la cama B
                relay_b = Relay(
                    room=str(room_id),
                    bed='B',
                    ip_address=f"192.168.{floor}.{room_num + 50}",  # Usamos +50 para diferenciar las camas
                    endpoint='/relay/0',
                    active=True
                )
                relays.append(relay_b)
        
        # Agregar todos los relés a la base de datos
        for relay in relays:
            db.session.add(relay)
        
        # Commit para aplicar los cambios en la base de datos
        db.session.commit()
        
        print("Base de datos inicializada con datos de prueba.")
        print("Usuario administrador: admin / admin123")
        print("Usuario regular: user / user123")
        print("Códigos de los asistentes activos:", ", ".join([a.code for a in assistants if a.active]))
        print("Usuarios de asistentes creados con contraseña por defecto: PPP2025")
        print("Nombres de usuario de asistentes:", ", ".join([f"{a.name}" for a in assistants]))
        print(f"Se crearon {len(relays)} relés para las habitaciones y camas")

if __name__ == '__main__':
    init_db() 