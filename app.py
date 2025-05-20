#!/usr/bin/env python
from app import create_app, db
from app.models.models import User, Assistant, Call

app = create_app()

# Eliminamos before_first_request ya que es obsoleto y no funciona bien con múltiples workers
# Utilizaremos los scripts de inicialización de base de datos en su lugar

def create_tables():
    """Función para crear las tablas si no existen (para usar en scripts)"""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    print("Iniciando Sistema de Llamadas Paciente-Enfermero...")
    print("Acceder a http://localhost:5000 para usar la aplicación")
    # Crear tablas en modo desarrollo
    create_tables()
    app.run(host='0.0.0.0', port=5000, debug=True) 