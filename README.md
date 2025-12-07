# Ticketera Prime - Sistema HelpDesk

**Ticketera Prime** es una plataforma completa de **HelpDesk (Mesa de Ayuda)** diseñada como Proyecto de Título para la Asignatura Capstone de Duoc UC.

El objetivo principal es solucionar la falta de un sistema formal para la gestión de solicitudes de soporte técnico en instituciones educativas. Se reemplaza la gestión informal (correos, solicitudes verbales) por una plataforma centralizada que asegura la trazabilidad, optimiza la atención y permite medir la eficiencia del servicio.

* **Estado del Proyecto:** Completado (Web + Mobile)
* **Metodología:** Agile (Scrum adaptado a equipo de 2 personas)
* **Versión Actual:** 1.0.0

## Características Principales

### Aplicación Web
* **Gestión Completa de Tickets:** Creación, asignación, seguimiento y cierre de solicitudes de soporte
* **Sistema de Roles y Permisos:** 
    * **Docente:** Crea tickets y consulta el estado de sus solicitudes
    * **Técnico (TI):** Gestiona tickets asignados, añade comentarios y actualiza estados
    * **Administrador:** Control total - asigna tickets, gestiona usuarios y accede a métricas
* **Dashboard Analítico (KPIs):** 
    * Tickets Abiertos vs. En Progreso
    * Seguimiento de SLA (Acuerdo de Nivel de Servicio)
    * Tiempo de Respuesta Promedio
    * Gráficos interactivos (Chart.js): por Estado, Categoría y Prioridad
* **Sistema de Notificaciones:** Notificaciones en tiempo real con Django Signals
* **Reportes Avanzados:** Filtros por fecha, categoría, estado y prioridad
* **Diseño Responsive:** Interfaz adaptativa para PC y móviles

### Aplicación Móvil (Flutter)
* **Multiplataforma:** Android (iOS compatible)
* **Auto-detección de Servidor:** Conexión automática a producción o desarrollo local
* **Login Seguro:** Autenticación con token persistente
* **Gestión de Tickets:** Creación, visualización y comentarios
* **Notificaciones Push:** Alertas de nuevas asignaciones y actualizaciones
* **Sincronización en Tiempo Real:** Cambios reflejados instantáneamente
* **Interfaz Nativa:** Diseño Material Design alineado con la versión web

## Stack de Tecnologías

### Backend
* **Framework:** Django 5.2.8 (Python 3.12)
* **API REST:** Django REST Framework 3.15.2
* **Base de Datos:** Microsoft SQL Server (Azure)
* **Autenticación:** Token-based authentication
* **CORS:** django-cors-headers para comunicación cross-origin

### Frontend Web
* **HTML5 / CSS3 / JavaScript Vanilla**
* **Chart.js:** Visualización de datos y gráficos
* **SweetAlert2:** Alertas y notificaciones
* **Responsive Design:** Media queries para adaptabilidad

### Aplicación Móvil
* **Framework:** Flutter 3.38.3 (Dart 3.10.1)
* **HTTP Client:** package:http para comunicación API
* **Persistencia:** SharedPreferences para almacenamiento local
* **State Management:** Provider
* **UI:** Material Design 3

### Infraestructura
* **Control de Versiones:** Git / GitHub
* **Variables de Entorno:** python-dotenv
* **Hosting Backend:** Compatible con Cloudflare Tunnel
* **Base de Datos:** SQL Server Azure 

## Instalación de la App Móvil

### Descargar APK
Descarga la última versión desde la sección [Releases](https://github.com/LDemons/Ticketera_Prime/releases):
- **Versión Actual:** v1.0.0
- **Archivo:** `Ticketera_Prime_v1.0.0.apk` (46.9 MB)

### Instalación en Android
1. Descarga el archivo APK desde Releases
2. Transfiere el archivo a tu dispositivo Android (si lo descargaste en PC)
3. Abre **Configuración > Seguridad** y habilita "Instalar apps de origen desconocido" o "Fuentes desconocidas"
4. Localiza el archivo APK en tu dispositivo usando un explorador de archivos
5. Toca el archivo APK y sigue las instrucciones en pantalla
6. Una vez instalada, abre la app e inicia sesión con tus credenciales

### Credenciales por Defecto
Los nuevos usuarios creados por el administrador tienen la contraseña: **ticketera2025**
Se recomienda cambiar la contraseña después del primer inicio de sesión desde el panel web.

## Seguridad

- Autenticación basada en tokens
- CORS configurado para comunicación segura
- Variables de entorno para credenciales sensibles
- HTTPS en producción (Cloudflare Tunnel)
- Validación de permisos por rol

## Documentación API

La documentación completa de la API REST está disponible en:
- `API_DOCUMENTATION.md` - Referencia completa de endpoints
- `RESUMEN_API.md` - Guía rápida de uso

## Autores

Este proyecto fue desarrollado por:

* **Cristian Silva** - Administrador de Proyecto / Scrum Master
* **Ignacio Hernández** - Desarrollador Full Stack

## Licencia

Proyecto de Título - Duoc UC © 2025