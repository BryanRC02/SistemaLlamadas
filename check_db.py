import pymysql
from app import create_app, db
from app.models.models import User, Assistant, Call

app = create_app()

def check_db():
    with app.app_context():
        # Verificar conexión a la base de datos
        try:
            # Obtener estadísticas de las tablas
            users_count = User.query.count()
            assistants_count = Assistant.query.count()
            calls_count = Call.query.count()
            
            print(f"Conexión exitosa a la base de datos MariaDB")
            print(f"Tablas encontradas:")
            print(f"- user: {users_count} registros")
            print(f"- assistant: {assistants_count} registros")
            print(f"- call: {calls_count} registros")
            
            # Mostrar usuarios
            print("\nUsuarios:")
            users = User.query.all()
            for user in users:
                print(f"- {user.username} (Admin: {user.is_admin})")
            
            # Mostrar asistentes
            print("\nAsistentes:")
            assistants = Assistant.query.all()
            for assistant in assistants:
                print(f"- {assistant.name} (Código: {assistant.code}, Activo: {assistant.active})")
            
            # Mostrar algunas llamadas
            print("\nLlamadas recientes:")
            calls = Call.query.order_by(Call.call_time.desc()).limit(3).all()
            for call in calls:
                print(f"- Habitación {call.room}-{call.bed}, Estado: {call.status}")
            
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")

if __name__ == '__main__':
    check_db() 