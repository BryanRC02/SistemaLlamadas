# Configuración de Gmail para Sistema de Llamadas

Este documento explica cómo configurar el Sistema de Llamadas para utilizar Gmail como servidor de correo electrónico.

## Requisitos previos

1. Una cuenta de Gmail
2. Si tienes habilitada la verificación en dos pasos (2FA), necesitarás crear una contraseña de aplicación

## Configuración de variables de entorno

Para configurar el sistema para usar Gmail, debes establecer las siguientes variables de entorno:

```bash
# Variables para Gmail
export MAIL_USERNAME="tu_correo@gmail.com"
export MAIL_PASSWORD="tu_contraseña_o_contraseña_de_aplicacion"
export MAIL_DEFAULT_SENDER="tu_correo@gmail.com"
```

Puedes añadir estas líneas al archivo `.env` en la raíz del proyecto o configurarlas directamente en tu sistema.

## Crear una contraseña de aplicación (recomendado)

Si tienes habilitada la verificación en dos pasos en tu cuenta de Google, debes crear una contraseña de aplicación:

1. Ve a tu cuenta de Google: [https://myaccount.google.com/](https://myaccount.google.com/)
2. Selecciona "Seguridad" en el menú lateral
3. En la sección "Acceso a Google", selecciona "Contraseñas de aplicaciones"
4. Selecciona "Otra" en el menú desplegable y escribe "Sistema de Llamadas"
5. Haz clic en "Generar"
6. Google te proporcionará una contraseña de 16 caracteres. Cópiala y úsala como valor para `MAIL_PASSWORD`

## Permitir aplicaciones menos seguras (alternativa no recomendada)

Si no tienes habilitada la verificación en dos pasos, deberás permitir el acceso de aplicaciones menos seguras:

1. Ve a [https://myaccount.google.com/lesssecureapps](https://myaccount.google.com/lesssecureapps)
2. Activa la opción "Permitir el acceso de aplicaciones menos seguras"

**Nota**: Google está eliminando gradualmente esta opción, por lo que se recomienda usar contraseñas de aplicación.

## Probar la configuración

Una vez configuradas las variables de entorno:

1. Inicia el sistema
2. Accede al panel de administración
3. Haz clic en el botón "Probar Correo" en la página de gestión de asistentes
4. Ingresa un correo electrónico de destino y envía el correo de prueba

Si todo está configurado correctamente, deberías recibir el correo de prueba en la dirección especificada. 