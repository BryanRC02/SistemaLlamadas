from app import create_app, db
from app.models.models import User, Assistant, Call
from datetime import datetime, timedelta
import random

app = create_app()

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if we already have data
        if User.query.count() > 0:
            print("Database already initialized. Skipping.")
            return
        
        # Create admin user
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create regular user
        user = User(username='user', email='user@example.com')
        user.set_password('user123')
        db.session.add(user)
        
        # Create assistants
        assistants = [
            Assistant(name='Juan Pérez', code='ABC123', active=True),
            Assistant(name='María García', code='DEF456', active=True),
            Assistant(name='Carlos López', code='GHI789', active=True),
            Assistant(name='Ana Martínez', code='JKL012', active=True),
            Assistant(name='Pedro Rodríguez', code='MNO345', active=False)
        ]
        
        for assistant in assistants:
            db.session.add(assistant)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create some calls
        now = datetime.utcnow()
        
        # Pending calls
        for i in range(3):
            room = random.randint(101, 105)
            bed = random.choice(['a', 'b'])
            call = Call(room=str(room), bed=bed, call_time=now - timedelta(minutes=random.randint(5, 30)), status='pending')
            db.session.add(call)
        
        # Attending calls
        for i in range(2):
            room = random.randint(101, 105)
            bed = random.choice(['a', 'b'])
            assistant = random.choice(assistants[:4])  # Only active assistants
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
        
        # Completed calls
        for i in range(5):
            room = random.randint(101, 105)
            bed = random.choice(['a', 'b'])
            assistant = random.choice(assistants[:4])  # Only active assistants
            call_time = now - timedelta(minutes=random.randint(60, 1440))  # Up to 24 hours ago
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
        
        # Commit all changes
        db.session.commit()
        
        print("Database initialized with test data.")
        print("Admin user: admin / admin123")
        print("Regular user: user / user123")
        print("Assistant codes:", ", ".join([a.code for a in assistants if a.active]))

if __name__ == '__main__':
    init_db() 