# Guía de Instalación del Sistema de Llamadas Paciente-Enfermero

Este documento proporciona las instrucciones paso a paso para instalar y configurar el Sistema de Llamadas Paciente-Enfermero en un servidor Linux.

## Requisitos Previos

1. Sistema operativo Linux (Ubuntu 20.04 LTS o superior recomendado)
2. Python 3.8 o superior
3. MariaDB 10.5 o superior
4. Nginx
5. Supervisor (opcional, para gestión de procesos)

## Instalación de Dependencias

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3 python3-pip python3-venv mariadb-server nginx supervisor

# Iniciar y habilitar MariaDB
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Configurar MariaDB (siga los pasos en pantalla)
sudo mysql_secure_installation
```

## Configuración de MariaDB

```bash
# Acceder a MariaDB
sudo mysql -u root -p

# Crear base de datos y usuario
CREATE DATABASE sistemallamadas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'ppp2025';
GRANT ALL PRIVILEGES ON sistemallamadas.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Instalación del Sistema

```bash
# Clonar repositorio o copiar archivos
git clone <URL_REPOSITORIO> /opt/SistemaLlamadas
cd /opt/SistemaLlamadas

# Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias Python
pip install -r requirements.txt

# Inicializar base de datos
python init_db.py
```

## Configuración del Servicio

1. Copiar archivo de servicio:

```bash
sudo cp sistemallamadas.service.example /etc/systemd/system/sistemallamadas.service
```

2. Editar el archivo y modificar las rutas según sea necesario:

```bash
sudo nano /etc/systemd/system/sistemallamadas.service
```

3. Habilitar e iniciar el servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sistemallamadas
sudo systemctl start sistemallamadas
```

## Configuración de Nginx

1. Copiar archivo de configuración:

```bash
sudo cp nginx.conf.example /etc/nginx/sites-available/sistemallamadas
```

2. Editar y ajustar según necesidades:

```bash
sudo nano /etc/nginx/sites-available/sistemallamadas
```

3. Activar configuración:

```bash
sudo ln -s /etc/nginx/sites-available/sistemallamadas /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Opcional: eliminar configuración por defecto
```

4. Verificar y reiniciar:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

## Creación de Directorios de Log

```bash
# Crear directorio de logs
sudo mkdir -p /var/log/sistemallamadas
sudo chown www-data:www-data /var/log/sistemallamadas
```

## Configuración de Pushover

Para recibir notificaciones, regístrese en [Pushover](https://pushover.net/) y actualice los valores de token y clave de usuario en el archivo `config.py`.

## Verificación de la Instalación

1. Comprobar estado del servicio:

```bash
sudo systemctl status sistemallamadas
```

2. Verificar logs:

```bash
tail -f /var/log/sistemallamadas/error.log
```

3. Acceder a la aplicación web:
   - http://IP_DEL_SERVIDOR/
   - http://IP_DEL_SERVIDOR/admin (para administradores)

## Configuración de Red

Asegúrese de configurar correctamente la red para que:

1. Los pulsadores WiFi puedan acceder al servidor en el puerto 80 (http)
2. El servidor pueda acceder a los relés WiFi en sus respectivas direcciones IP
3. Si es necesario, configure direcciones IP estáticas para los dispositivos

## Configuración de Pulsadores y Relés

### Pulsadores WiFi
Configurar para enviar peticiones HTTP GET a:
- Llamada: `http://IP_SERVIDOR/llamada/<habitación>/<cama>`
- Presencia: `http://IP_SERVIDOR/presencia/<habitación>/<cama>`

### Relés WiFi
Configurar con dirección IP estática en el formato:
- `172.17.2.<número_habitación>`

## Mantenimiento

1. Actualizar el sistema periódicamente:

```bash
cd /opt/SistemaLlamadas
source venv/bin/activate
git pull  # Si usa control de versiones
pip install -r requirements.txt
sudo systemctl restart sistemallamadas
```

2. Copias de seguridad regulares:

```bash
# Backup de base de datos
mysqldump -u admin -p sistemallamadas > backup_$(date +%Y%m%d).sql
``` 