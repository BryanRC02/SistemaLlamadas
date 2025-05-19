#!/usr/bin/env python
from app import create_app, db
from app.models.models import User, Assistant, Call

app = create_app()

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    print("Iniciando Sistema de Llamadas Paciente-Enfermero...")
    print("Acceder a http://localhost:5000 para usar la aplicación")
    app.run(host='0.0.0.0', port=5000, debug=True) 