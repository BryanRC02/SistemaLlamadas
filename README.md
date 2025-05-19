# Sistema de Llamadas Paciente-Enfermero

Este es un sistema básico pero funcional para gestionar llamadas entre pacientes y enfermeros en un centro de atención sanitaria.

## Características

- Registro de llamadas de pacientes
- Notificaciones a asistentes mediante Pushover
- Control de luces indicadoras en habitaciones
- Gestión de asistentes
- Histórico de llamadas y asistencias
- Exportación de datos en CSV

## Requisitos

- Python 3.7+
- Flask y dependencias (ver requirements.txt)
- Cuenta de Pushover para notificaciones

## Instalación

1. Clonar este repositorio
2. Crear un entorno virtual: `python -m venv venv`
3. Activar el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`
5. Configurar variables de entorno (opcional):
   - `SECRET_KEY`: Clave secreta para la aplicación
   - `DATABASE_URL`: URL de la base de datos (por defecto SQLite)
   - `PUSHOVER_API_TOKEN`: Token de API de Pushover
   - `PUSHOVER_USER_KEY`: Clave de usuario de Pushover

## Uso

1. Ejecutar la aplicación: `python app.py`
2. Acceder a la aplicación en `http://localhost:5000`
3. Registrar un usuario (el primer usuario será administrador)
4. Crear asistentes en el panel de administración
5. Los asistentes pueden enrolarse con su código en `/enroll`

## Estructura de la Aplicación

- `app/`: Directorio principal de la aplicación
  - `models/`: Modelos de la base de datos
  - `routes/`: Rutas de la aplicación
  - `templates/`: Plantillas HTML
  - `static/`: Archivos estáticos (CSS, JS, etc.)
- `config.py`: Configuración de la aplicación
- `app.py`: Punto de entrada de la aplicación

## API REST

- `GET /llamada/<room>/<bed>`: Registra una llamada de un paciente
- `GET /presencia/<room>/<bed>`: Registra la presencia de un asistente
- `GET /atender/<call_id>`: Atiende una llamada

## Presupuesto Estimado

Para un edificio de 5 plantas con 10 habitaciones por planta y 2 camas por habitación:

- 100 pulsadores WiFi (2 por cama): 100 × 70€ = 7,000€
- 100 relés WiFi (1 por cama): 100 × 60€ = 6,000€
- 12 dispositivos Android para asistentes: 12 × 150€ = 1,800€
- 12 licencias Pushover: 12 × 5$ ≈ 60€
- Servidor: 1,000€
- Desarrollo e implementación: 5,000€
- Mantenimiento anual: 2,000€

**Total aproximado**: 22,860€

## Licencia

Este proyecto está bajo la Licencia MIT. 