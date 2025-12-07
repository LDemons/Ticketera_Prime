# Changelog

Todas las actualizaciones notables del proyecto serán documentadas en este archivo.

## [1.0.0] - 2025-12-07

### Aplicación Móvil
#### Agregado
- Auto-detección de servidor (producción y desarrollo local)
- Gestión completa de tickets desde dispositivos móviles
- Sistema de notificaciones en tiempo real
- Sincronización automática con el servidor
- Interfaz Material Design nativa

#### Corregido
- Problema de codificación UTF-8 en textos en español (acentos y caracteres especiales)
- Conexión automática a servidor local para desarrollo
- Persistencia de token de autenticación

### Backend
#### Agregado
- Signal automático para crear Django User al crear Usuario en la app
- Contraseña por defecto "ticketera2025" para nuevos usuarios
- Sincronización automática entre tablas Usuario y Django User
- Script de verificación de sincronización de usuarios

#### Corregido
- Sincronización de contraseñas entre modelo Usuario y Django User
- Login móvil con usuarios creados desde el panel web
- Actualización de contraseñas desde cambiar_contrasenia_ajax

### Seguridad
- Migración de SECRET_KEY a variables de entorno
- Eliminación de IPs hardcodeadas en código fuente
- Configuración segura de CORS para producción

### Documentación
- README actualizado con instrucciones de instalación APK
- Documentación de credenciales por defecto
- Limpieza de emojis en scripts Python
- API_DOCUMENTATION.md actualizada

## Notas de Versión

### Características Principales
- Sistema completo de HelpDesk con gestión de tickets
- Aplicación web responsive con dashboard analítico
- Aplicación móvil nativa para Android
- Sistema de roles (Docente, TI, Admin, Superadmin)
- Notificaciones en tiempo real
- Reportes y métricas avanzadas

### Requisitos
- Android 5.0 (API 21) o superior para la app móvil
- Python 3.12 para el backend
- SQL Server (Azure) para la base de datos

### Instalación
Consulta el README.md para instrucciones detalladas de instalación.
