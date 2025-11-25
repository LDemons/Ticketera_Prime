# API REST Implementada - Resumen de Cambios

## Archivos Creados

### 1. **tickets/serializers.py** (NUEVO)
Contiene todos los serializers para convertir modelos Django a JSON:
- `UsuarioSerializer` - Datos de usuario
- `CategoriaSerializer` - Categorías de tickets
- `PrioridadSerializer` - Niveles de prioridad
- `ComentarioSerializer` - Comentarios de tickets
- `TicketListSerializer` - Vista simplificada de tickets (lista)
- `TicketDetailSerializer` - Vista completa de ticket (detalle)
- `TicketCreateSerializer` - Crear nuevos tickets
- `NotificacionSerializer` - Notificaciones
- `ComentarioCreateSerializer` - Crear comentarios

### 2. **tickets/api_views.py** (NUEVO)
Contiene todas las vistas de la API:
- `CustomAuthToken` - Login con email/password → devuelve token
- `TicketViewSet` - CRUD de tickets + comentarios + fijar
- `NotificacionViewSet` - Listar y marcar notificaciones como leídas
- `CategoriaListView` - Listar categorías
- `PrioridadListView` - Listar prioridades
- `user_profile()` - Perfil del usuario autenticado
- `dashboard_stats()` - Estadísticas del dashboard

### 3. **tickets/api_urls.py** (NUEVO)
Define todas las rutas de la API:
- `/api/v1/auth/login/` - Login
- `/api/v1/auth/profile/` - Perfil usuario
- `/api/v1/tickets/` - CRUD tickets
- `/api/v1/tickets/{id}/add_comment/` - Añadir comentario
- `/api/v1/tickets/{id}/toggle_pin/` - Fijar/desfijar
- `/api/v1/notificaciones/` - Notificaciones
- `/api/v1/categorias/` - Categorías
- `/api/v1/prioridades/` - Prioridades
- `/api/v1/stats/` - Estadísticas

### 4. **API_DOCUMENTATION.md** (NUEVO)
Documentación completa de la API con:
- Explicación de autenticación
- Todos los endpoints disponibles
- Ejemplos de request/response
- Ejemplos en Flutter/cURL
- Códigos de error
- Flujo completo de uso

---

## Archivos Modificados

### 1. **ticketera_project/settings.py**
Agregado `rest_framework` y `rest_framework.authtoken` a `INSTALLED_APPS`
Agregada configuración `REST_FRAMEWORK`:
- Autenticación por Token
- Paginación de 20 items
- Solo respuestas JSON

### 2. **ticketera_project/urls.py**
Agregada ruta `path('api/v1/', include('tickets.api_urls'))`

### 3. **requirements.txt**
Agregadas nuevas dependencias:
- `djangorestframework`
- `djangorestframework-simplejwt`
- `python-dotenv`

---

## Base de Datos

Ejecutadas migraciones para:
- `authtoken.0001_initial`
- `authtoken.0002_auto_20160226_1747`
- `authtoken.0003_tokenproxy`
- `authtoken.0004_alter_tokenproxy_options`

Esto crea la tabla `authtoken_token` para almacenar los tokens de autenticación.

---

## Funcionalidades Implementadas

### Autenticación
- [x] Login con email y contraseña
- [x] Generación automática de tokens
- [x] Validación de usuario activo
- [x] Autenticación por token en todos los endpoints

### Gestión de Tickets
- [x] Listar tickets (filtrado por rol)
  - Docente: Solo sus tickets
  - TI: Tickets asignados
  - Admin: Todos los tickets
- [x] Crear ticket (solo Docente)
- [x] Ver detalle de ticket
- [x] Añadir comentarios
- [x] Fijar/desfijar tickets (solo TI)

### Notificaciones
- [x] Listar notificaciones del usuario
- [x] Marcar notificación como leída
- [x] Marcar todas las notificaciones como leídas

### Dashboard
- [x] Estadísticas por rol
  - Docente: Total, abiertos, en progreso, resueltos, cerrados
  - TI: Incluye también tickets fijados

### Datos Auxiliares
- [x] Listar categorías
- [x] Listar prioridades
- [x] Perfil del usuario

---

## Cómo Usar la API

### 1. Iniciar servidor (desarrollo)
```bash
python manage.py runserver
```

### 2. Obtener token (Login)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "docente@colegio.cl", "password": "tu_password"}'
```

### 3. Usar el token en requests
```bash
curl -X GET http://localhost:8000/api/v1/tickets/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

---

## Siguiente Paso: Desarrollo App Móvil

Ahora puedes desarrollar la app móvil con:

### Opción 1: Flutter (Recomendado)
```dart
// Ejemplo de consumo de API
import 'package:http/http.dart' as http;

final response = await http.get(
  Uri.parse('http://ticketeraprime.com/api/v1/tickets/'),
  headers: {'Authorization': 'Token $token'},
);
```

### Opción 2: React Native
```javascript
// Ejemplo de consumo de API
const response = await fetch('http://ticketeraprime.com/api/v1/tickets/', {
  headers: {
    'Authorization': `Token ${token}`,
  },
});
```

### Opción 3: Kotlin/Swift (Nativo)
```kotlin
// Ejemplo para Android
val request = Request.Builder()
    .url("http://ticketeraprime.com/api/v1/tickets/")
    .addHeader("Authorization", "Token $token")
    .build()
```

---

## Características de la App Móvil Sugeridas

### Pantallas Docente:
1. **Login** - Autenticación
2. **Dashboard** - Estadísticas de mis tickets
3. **Mis Tickets** - Lista de tickets
4. **Crear Ticket** - Formulario con categoría y prioridad
5. **Detalle Ticket** - Ver y comentar
6. **Notificaciones** - Lista de notificaciones

### Pantallas TI:
1. **Login** - Autenticación
2. **Dashboard** - Estadísticas de asignaciones
3. **Mis Asignaciones** - Lista de tickets asignados
4. **Detalle Ticket** - Ver, comentar y fijar
5. **Notificaciones** - Lista de notificaciones

---

## Configuración para Producción

Cuando despliegues la app móvil, recuerda:

1. **Cambiar URL base** de `localhost` a tu dominio
2. **Configurar HTTPS** (obligatorio para apps móviles)
3. **Configurar CORS** si es necesario:
   ```bash
   pip install django-cors-headers
   ```
4. **Implementar refresh tokens** para seguridad adicional
5. **Configurar notificaciones push** (Firebase/OneSignal)

---

## Ventajas de esta Implementación

**Separación clara** entre web y móvil
**Autenticación robusta** con tokens
**Permisos por rol** automáticos
**Paginación** incluida
**Validaciones** en serializers
**Documentación completa**
**Fácil de extender** (agregar más endpoints)
**RESTful** siguiendo mejores prácticas

---

## Recursos Útiles

- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [Flutter HTTP Package](https://pub.dev/packages/http)
- [React Native Fetch API](https://reactnative.dev/docs/network)
- [Postman](https://www.postman.com/) - Para testear la API

---

## Troubleshooting

### Error: "No module named 'rest_framework'"
```bash
pip install djangorestframework
```

### Error: "Invalid token"
Verifica que estés enviando el header correcto:
```
Authorization: Token {tu_token}
```

### Error 403 Forbidden
Verifica que el usuario tenga los permisos correctos para la acción.

---

## Estado Actual

**Backend API REST**: 100% completo y funcional
**App Móvil**: Pendiente (siguiente fase)
**Plataformas soportadas**: iOS + Android (cuando uses Flutter/React Native)

---

## Sugerencias Adicionales

1. **Implementar refresh tokens** para mayor seguridad
2. **Agregar filtros** a los endpoints (por estado, fecha, etc.)
3. **Implementar búsqueda** de tickets
4. **Agregar paginación customizable** (más o menos items)
5. **Implementar rate limiting** para prevenir abuso
6. **Agregar versionado** de la API (v2, v3, etc.)
7. **Implementar WebSockets** para notificaciones en tiempo real

---

La API está lista para ser consumida por tu aplicación móvil.
