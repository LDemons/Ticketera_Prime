# Ticketera Prime (Proyecto de Título)

**Ticketera Prime** es una plataforma de software de **HelpDesk (Mesa de Ayuda)** diseñada como un Proyecto de Título para la Asignatura Capstone de Duoc UC.

El objetivo principal es solucionar la falta de un sistema formal para la gestión de solicitudes de soporte técnico en instituciones educativas. Se reemplaza la gestión informal (correos, solicitudes verbales) por una plataforma centralizada que asegura la trazabilidad, optimiza la atención y permite medir la eficiencia del servicio.

* **Estado del Proyecto:** Fase 2/3 (Aplicación Web/MVP completada).
* **Metodología:** Agile (Scrum adaptado a un equipo de 2 personas).

## Características Principales

* **Gestión de Tickets:** Creación, asignación, seguimiento y cierre de solicitudes de soporte (incidencias).
* **Roles y Permisos:** Vistas y funcionalidades diferenciadas para tres perfiles de usuario:
    * **Docente (Usuario Final):** Puede crear tickets y ver el estado de sus solicitudes.
    * **Técnico (Agente TI):** Gestiona los tickets que le son asignados, añade comentarios y cambia estados.
    * **Administrador:** Tiene control total, asigna tickets, gestiona usuarios y ve métricas.
* **Dashboard de Métricas (KPIs):** Panel visual para el Admin que muestra indicadores clave del HelpDesk, tales como:
    * Tickets Abiertos vs. En Progreso.
    * Tickets con **SLA Vencidos** (Acuerdo de Nivel de Servicio).
    * Tiempo de Respuesta Promedio.
    * Gráficos de Tickets por Estado, Categoría y Prioridad.
* **Notificaciones Automáticas:** El sistema genera notificaciones internas (usando Django Signals) cuando se asigna un ticket o se añade un comentario.
* **Reportes Simples:** Módulo de reportes filtrables por fecha para analizar la carga de trabajo por categoría, estado y prioridad.
* **Aplicación Móvil (Planificada):** El alcance del proyecto incluye una app móvil básica para que los docentes puedan crear y consultar tickets.

## Stack de Tecnologías

| Área | Tecnología |
| :--- | :--- |
| **Backend** | **Python 3** con **Django 5.2.6** |
| **Base de Datos** | **Microsoft SQL Server** (conectado vía `django-mssql-backend`) |
| **Frontend** | HTML5, CSS3 (Vanilla), JavaScript |
| **Librerías JS** | `Chart.js` (para gráficos) y `SweetAlert2` (para alertas) |
| **Dependencias** | `python-dotenv` (para gestión de variables de entorno) |

## Autores

Este proyecto fue desarrollado por:

* **Cristian Silva:** Administrador de Proyecto / Scrum Master
* **Ignacio Hernández:** Desarrollador Full Stack