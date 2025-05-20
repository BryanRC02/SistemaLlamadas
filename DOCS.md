# Documentación del Sistema de Llamadas Paciente-Enfermero

## Arquitectura del Sistema

El sistema está compuesto por los siguientes componentes:

1. **Servidor de Aplicaciones**: Implementado con Flask, gestiona las solicitudes HTTP de los pulsadores y pilotos, y ofrece la interfaz web para la gestión del sistema.

2. **Base de Datos**: Almacena información sobre usuarios, asistentes y llamadas.

3. **Dispositivos en Habitaciones**:
   - Pulsadores WiFi que envían solicitudes HTTP al servidor.
   - Relés WiFi que controlan los pilotos luminosos.

4. **Dispositivos de Asistentes**:
   - Smartphones con la aplicación Pushover instalada.

## Sistema de Relés

El sistema incluye la capacidad de integración con relés WiFi para controlar luces indicadoras en las habitaciones de los pacientes. Cada habitación cuenta con dos pulsadores:

1. **Pulsador de Llamada**: Para que el paciente solicite asistencia.
2. **Pulsador de Presencia**: Para que el asistente confirme que está en la habitación.

### Rutas HTTP para los Pulsadores

- **Llamada**:
  ```
  GET http://[SERVER_IP]/llamada/[ROOM]/[BED]
  ```
  Ejemplo: `http://172.17.0.10/llamada/104/b`

- **Presencia**:
  ```
  GET http://[SERVER_IP]/presencia/[ROOM]/[BED]
  ```
  Ejemplo: `http://172.17.0.10/presencia/104/b`

### Control de Relés

El sistema controla pilotos luminosos en cada habitación a través de relés WiFi:

- **Encender Piloto**:
  ```
  GET http://172.17.2.[ROOM]/relay/0?turn=on
  ```
  Ejemplo: `http://172.17.2.104/relay/0?turn=on`

- **Apagar Piloto**:
  ```
  GET http://172.17.2.[ROOM]/relay/0?turn=off
  ```
  Ejemplo: `http://172.17.2.104/relay/0?turn=off`

### Flujo de Funcionamiento

1. El paciente pulsa el botón de llamada, generando una solicitud HTTP al servidor.
2. El sistema registra la llamada y envía una notificación a los asistentes.
3. Cuando un asistente confirma la recepción de la llamada a través de la app de Pushover, el sistema enciende el piloto luminoso de la habitación.
4. Una vez que el asistente llega a la habitación, presiona el botón de presencia, generando otra solicitud HTTP.
5. El sistema marca la llamada como completada y apaga el piloto luminoso.

### Endpoints de Prueba

Para probar el sistema sin hardware real, se han implementado los siguientes endpoints:

- **Simular Llamada**:
  ```
  GET /test/simulate/llamada/[ROOM]/[BED]
  ```

- **Simular Presencia**:
  ```
  GET /test/simulate/presencia/[ROOM]/[BED]
  ```

- **Probar Relé**:
  ```
  GET /test/relay/[ROOM]/[ACTION]
  ```
  Donde `[ACTION]` puede ser `on` u `off`.

## Flujo de Funcionamiento

1. **Llamada del Paciente**:
   - El paciente pulsa el botón junto a su cama.
   - El pulsador WiFi envía una solicitud HTTP al servidor: `/llamada/<habitación>/<cama>`
   - El servidor registra la llamada en la base de datos.
   - El servidor envía una notificación a todos los dispositivos de asistentes mediante Pushover.

2. **Atención de la Llamada**:
   - El asistente recibe la notificación en su smartphone.
   - El asistente pulsa en el enlace "Atender solicitud de asistencia".
   - El servidor registra qué asistente atenderá la llamada.
   - El servidor envía una solicitud HTTP al relé para encender el piloto: `/relay/0?turn=on`.

3. **Presencia en Habitación**:
   - El asistente llega a la habitación y pulsa el botón de presencia.
   - El pulsador WiFi envía una solicitud HTTP al servidor: `/presencia/<habitación>/<cama>`
   - El servidor registra la presencia y completa la llamada.
   - El servidor envía una solicitud HTTP al relé para apagar el piloto: `/relay/0?turn=off`.

## Configuración de Dispositivos

### Pulsadores WiFi

Los pulsadores WiFi deben configurarse para enviar solicitudes HTTP GET a las siguientes URLs:

- Botón de llamada: `http://<IP_SERVIDOR>/llamada/<habitación>/<cama>`
- Botón de presencia: `http://<IP_SERVIDOR>/presencia/<habitación>/<cama>`

### Relés WiFi

Los relés WiFi deben configurarse con una dirección IP estática siguiendo el patrón:

`172.17.2.<número_habitación>`

Y deben responder a las siguientes URLs:

- Encender piloto: `http://<IP_RELÉ>/relay/0?turn=on`
- Apagar piloto: `http://<IP_RELÉ>/relay/0?turn=off`

## Configuración de Pushover

1. Crear una cuenta en [Pushover](https://pushover.net/)
2. Crear una aplicación para obtener el API Token
3. Configurar las variables de entorno:
   - `PUSHOVER_API_TOKEN`: Token de la aplicación
   - `PUSHOVER_USER_KEY`: Clave de usuario

## Mantenimiento

### Copias de Seguridad

Se recomienda realizar copias de seguridad diarias de la base de datos:

```bash
sqlite3 app.db .dump > backup_$(date +%Y%m%d).sql
```

### Monitorización

El sistema puede monitorizarse mediante:

- Logs del servidor: `/var/log/sistemallamadas/app.log`
- Estado del servicio: `systemctl status sistemallamadas`

## Solución de Problemas

### Problemas Comunes

1. **No se reciben notificaciones**:
   - Verificar la configuración de Pushover
   - Comprobar la conexión a Internet

2. **No se encienden/apagan los pilotos**:
   - Verificar la conectividad de los relés WiFi
   - Comprobar que las IPs de los relés son correctas

3. **No se registran las llamadas**:
   - Verificar la conectividad de los pulsadores WiFi
   - Comprobar que las URLs están correctamente configuradas 