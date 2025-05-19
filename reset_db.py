from app import create_app, db
from app.models.models import User, Assistant, Call

app = create_app()

def reset_db():
    with app.app_context():
        # Eliminar todas las tablas
        db.drop_all()
        print("Tablas eliminadas correctamente.")
        
        # Crear las tablas nuevamente
        db.create_all()
        print("Tablas creadas correctamente.")
        
        print("Base de datos reinicializada. Ejecute init_db.py para cargar datos de ejemplo.")

if __name__ == '__main__':
    reset_db() 