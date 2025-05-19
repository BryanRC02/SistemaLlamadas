# Estructura del Proyecto

Este documento describe la estructura de archivos y directorios del proyecto Sistema de Llamadas Paciente-Enfermero.

```
SistemaLlamadas/
│
├── app/                            # Directorio principal de la aplicación
│   ├── __init__.py                 # Inicialización de la aplicación Flask
│   ├── models/                     # Modelos de la base de datos
│   │   └── models.py               # Definición de las tablas y relaciones
│   ├── routes/                     # Rutas de la aplicación
│   │   ├── admin.py                # Rutas para administración de asistentes
│   │   ├── api.py                  # API REST para pulsadores y pilotos
│   │   ├── auth.py                 # Rutas de autenticación
│   │   └── main.py                 # Rutas principales
│   ├── static/                     # Archivos estáticos (CSS, JS, imágenes)
│   └── templates/                  # Plantillas HTML
│       ├── admin/                  # Plantillas para administración
│       │   ├── assistants.html     # Lista de asistentes
│       │   ├── edit_assistant.html # Edición de asistentes
│       │   └── new_assistant.html  # Creación de asistentes
│       ├── asistencias.html        # Histórico de asistencias
│       ├── base.html               # Plantilla base
│       ├── dashboard.html          # Panel de control
│       ├── enroll.html             # Enrolamiento de asistentes
│       ├── login.html              # Inicio de sesión
│       └── register.html           # Registro de usuarios
│
├── app.py                          # Punto de entrada principal
├── config.py                       # Configuración de la aplicación
├── DOCS.md                         # Documentación detallada
├── ESTRUCTURA.md                   # Este archivo
├── .env.example                    # Ejemplo de variables de entorno
├── .gitignore                      # Archivos a ignorar por git
├── init_db.py                      # Script para inicializar la base de datos
├── nginx.conf.example              # Ejemplo de configuración de Nginx
├── presupuesto.md                  # Presupuesto detallado
├── README.md                       # Información general del proyecto
├── requirements.txt                # Dependencias del proyecto
├── run.py                          # Script para ejecutar la aplicación en desarrollo
├── setup.bat                       # Script de configuración para Windows
├── setup.sh                        # Script de configuración para Linux/Mac
├── sistemallamadas.service.example # Ejemplo de servicio systemd
├── start.sh                        # Script para iniciar la aplicación en producción
└── test_call.py                    # Script para simular llamadas
```

## Descripción de Componentes Principales

### Modelos

- `User`: Usuarios del sistema con autenticación
- `Assistant`: Asistentes que atienden las llamadas
- `Call`: Registro de llamadas y su estado

### Rutas

- `/`: Redirección al dashboard
- `/dashboard`: Panel de control principal
- `/asistencias`: Histórico de llamadas
- `/enroll`: Enrolamiento de asistentes
- `/desenroll`: Desenrolamiento de asistentes
- `/asistentes/*`: Gestión de asistentes (admin)
- `/login`, `/logout`, `/register`: Autenticación
- `/llamada/<room>/<bed>`: API para registrar llamadas
- `/presencia/<room>/<bed>`: API para registrar presencia
- `/atender/<call_id>`: API para atender llamadas

### Scripts

- `app.py`: Inicializa la aplicación
- `init_db.py`: Crea las tablas y datos iniciales
- `run.py`: Ejecuta la aplicación en modo desarrollo
- `start.sh`: Inicia la aplicación con gunicorn
- `setup.sh`/`setup.bat`: Configura el entorno de desarrollo 