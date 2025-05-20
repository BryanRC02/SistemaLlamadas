# Guía de Instalación del Sistema de Llamadas Paciente-Enfermero

Este documento proporciona las instrucciones paso a paso para instalar y configurar el Sistema de Llamadas Paciente-Enfermero en un servidor Linux.

## Requisitos Previos

1. Sistema operativo Linux (Ubuntu 20.04 LTS o superior recomendado)
2. Python 3.8 o superior
3. MariaDB 10.5 o superior
4. Nginx
5. Supervisor (opcional, para gestión de procesos)

## Configuración de Red

**Importante**: El sistema está configurado para usar las siguientes direcciones IP:

- Servidor de aplicaciones: **172.17.0.10** (donde corre nginx y Flask)
- Relés WiFi: **172.17.2.XXX** (donde XXX es el número de habitación)

Asegúrese de que su servidor tenga asignada la IP 172.17.0.10 o modifique los archivos de configuración según sea necesario.

## Instalación de Dependencias

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3 python3-pip python3-venv mariadb-server nginx supervisor

# Iniciar y habilitar servicios
sudo systemctl start mariadb
sudo systemctl enable mariadb
sudo systemctl start nginx
sudo systemctl enable nginx

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
# Crear directorio de la aplicación
sudo mkdir -p /opt/SistemaLlamadas
sudo chown $USER:$USER /opt/SistemaLlamadas

# Clonar repositorio o copiar archivos
git clone https://github.com/BryanRC02/SistemaLlamadas /opt/SistemaLlamadas
cd /opt/SistemaLlamadas

# Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias Python
pip install -r requirements.txt

# Inicializar base de datos
python init_db.py
```

## Configuración de Directorios

```bash
# Crear directorio de logs
sudo mkdir -p /var/log/sistemallamadas
sudo chown www-data:www-data /var/log/sistemallamadas

# Asignar permisos correctos a la aplicación
sudo chown -R www-data:www-data /opt/SistemaLlamadas
sudo chmod -R 755 /opt/SistemaLlamadas
```

## Configuración del Servicio

1. Copiar archivo de servicio:

```bash
sudo cp /opt/SistemaLlamadas/sistemallamadas.service.example /etc/systemd/system/sistemallamadas.service
```

2. Verificar que las rutas en el archivo de servicio sean correctas:

```bash
sudo nano /etc/systemd/system/sistemallamadas.service
```

Asegúrese de que todas las rutas apunten a `/opt/SistemaLlamadas` y el usuario sea `www-data`.

3. Habilitar e iniciar el servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sistemallamadas
sudo systemctl start sistemallamadas
```

## Configuración de Nginx

1. Copiar archivo de configuración:

```bash
sudo cp /opt/SistemaLlamadas/nginx.conf.example /etc/nginx/sites-available/sistemallamadas
```

2. Verificar que la configuración sea correcta:

```bash
sudo nano /etc/nginx/sites-available/sistemallamadas
```

Asegúrese de que `server_name` esté configurado como `172.17.0.10` y que las rutas estáticas apunten a `/opt/SistemaLlamadas/app/static`.

3. Crear archivo de autenticación básica para áreas protegidas:

```bash
sudo apt install apache2-utils  # Para instalar htpasswd
sudo mkdir -p /etc/nginx
sudo htpasswd -c /etc/nginx/.htpasswd admin  # Crear usuario 'admin'
```

4. Activar configuración:

```bash
sudo ln -s /etc/nginx/sites-available/sistemallamadas /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default  # Eliminar configuración por defecto
```

5. Verificar y reiniciar:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

## Configuración de Pushover

Para recibir notificaciones, regístrese en [Pushover](https://pushover.net/) y actualice los valores de token y clave de usuario en el archivo `config.py`:

```bash
# Editar archivo de configuración
sudo nano /opt/SistemaLlamadas/config.py
```

## Prueba del Sistema

1. Comprobar estado del servicio:

```bash
sudo systemctl status sistemallamadas
```

2. Verificar logs:

```bash
tail -f /var/log/sistemallamadas/error.log
```

3. Acceder a la aplicación web:
   - http://172.17.0.10/ (interfaz principal)
   - http://172.17.0.10/admin (para administradores)

## Prueba de Pulsadores y Relés

Para probar la funcionalidad sin hardware real, use los endpoints de prueba:

```bash
# Simular una llamada de la habitación 104, cama b
curl http://172.17.0.10/test/simulate/llamada/104/b

# Simular presencia en habitación 104, cama b
curl http://172.17.0.10/test/simulate/presencia/104/b

# Probar control directo de un relé (encender)
curl http://172.17.0.10/test/relay/104/on

# Probar control directo de un relé (apagar)
curl http://172.17.0.10/test/relay/104/off
```

## Configuración de Pulsadores y Relés

### Pulsadores WiFi
Configurar para enviar peticiones HTTP GET a:
- Llamada: `http://172.17.0.10/llamada/<habitación>/<cama>`
- Presencia: `http://172.17.0.10/presencia/<habitación>/<cama>`

### Relés WiFi
Configurar con dirección IP estática en el formato:
- `172.17.2.<número_habitación>`

Deben responder a:
- `http://172.17.2.<número_habitación>/relay/0?turn=on` (encender)
- `http://172.17.2.<número_habitación>/relay/0?turn=off` (apagar)

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
mysqldump -u admin -p sistemallamadas > /opt/backups/backup_$(date +%Y%m%d).sql
```

3. Rotación de logs:

```bash
# Crear archivo de configuración para logrotate
sudo nano /etc/logrotate.d/sistemallamadas
```

Contenido:
```
/var/log/sistemallamadas/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload sistemallamadas
    endscript
}
```

## Solución de Problemas

### Problemas Comunes

1. **No se puede acceder a la aplicación web**:
   - Verificar estado de nginx: `sudo systemctl status nginx`
   - Verificar logs de nginx: `sudo tail -f /var/log/nginx/error.log`
   - Comprobar firewall: `sudo ufw status`

2. **No se encienden/apagan los pilotos**:
   - Verificar conectividad a los relés: `ping 172.17.2.XXX`
   - Revisar logs de aplicación: `tail -f /var/log/sistemallamadas/error.log`

3. **Errores en la base de datos**:
   - Verificar estado de MariaDB: `sudo systemctl status mariadb`
   - Revisar conexión: `mysql -u admin -p -e "USE sistemallamadas; SHOW TABLES;"`

4. **Problemas con Pushover**:
   - Verificar token y clave de usuario en `config.py`
   - Comprobar conexión a Internet: `ping api.pushover.net`
