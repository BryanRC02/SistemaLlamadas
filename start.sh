#!/bin/bash
set -e

# Definir variables
APP_DIR="/opt/SistemaLlamadas"
LOG_DIR="/var/log/sistemallamadas"
VENV_DIR="$APP_DIR/venv"

# Verificar que estamos en el directorio correcto
if [ ! -d "$APP_DIR" ]; then
    echo "Error: El directorio $APP_DIR no existe."
    echo "Por favor, ejecuta este script desde el directorio correcto o ajusta la variable APP_DIR."
    exit 1
fi

# Cambiar al directorio de la aplicación
cd "$APP_DIR"

# Verificar y crear directorio de logs si no existe
if [ ! -d "$LOG_DIR" ]; then
    echo "Creando directorio de logs $LOG_DIR..."
    sudo mkdir -p "$LOG_DIR"
    sudo chown www-data:www-data "$LOG_DIR"
fi

# Activar el entorno virtual
echo "Activando entorno virtual..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: El entorno virtual no existe en $VENV_DIR"
    echo "Por favor, crea el entorno virtual con: python3 -m venv venv"
    exit 1
fi

source "$VENV_DIR/bin/activate"

# Verificar dependencias
echo "Verificando dependencias..."
if ! pip freeze | grep -q "Flask"; then
    echo "Error: Faltan dependencias. Por favor, instálalas con: pip install -r requirements.txt"
    exit 1
fi

# Inicializar base de datos si es necesario
echo "Inicializando base de datos..."
python init_db.py

# Verificar permisos del directorio de logs
echo "Verificando permisos del directorio de logs..."
if [ ! -w "$LOG_DIR" ]; then
    echo "Ajustando permisos del directorio de logs..."
    sudo chown www-data:www-data "$LOG_DIR"
fi

# Iniciar Gunicorn
echo "Iniciando el servidor Gunicorn..."
exec gunicorn --workers 4 \
    --timeout 60 \
    --access-logfile "$LOG_DIR/access.log" \
    --error-logfile "$LOG_DIR/error.log" \
    --bind 0.0.0.0:5000 \
    --worker-class=gthread \
    --threads=2 \
    "app:create_app()"

echo "El servidor se ha detenido." 