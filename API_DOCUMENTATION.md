# API REST - Ticketera Prime (App Móvil)

## Descripción General

Esta API REST proporciona todos los endpoints necesarios para la aplicación móvil de Ticketera Prime. Permite a los docentes crear y gestionar sus tickets, y a los técnicos TI visualizar y actualizar sus asignaciones.

## Autenticación

La API utiliza **Token Authentication**. Debes obtener un token mediante login y enviarlo en cada request.

### Login

**Importante:** Usa el **email** del usuario (no el username de Django) para iniciar sesión.

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "usuario@colegio.cl",
  "password": "tu_contraseña"
}
```

**Respuesta exitosa:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "rut": 12345678,
    "nombre": "Juan Pérez",
    "email": "usuario@colegio.cl",
    "rol": "Docente"
  }
}
```

### Uso del Token

Incluye el token en el header `Authorization` de cada request:

```http
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

---

## Endpoints Disponibles

### **Usuario**

#### Obtener perfil del usuario autenticado
```http
GET /api/v1/auth/profile/
Authorization: Token {tu_token}
```

**Respuesta:**
```json
{
  "rut": 12345678,
  "dv": "9",
  "nombre": "Juan Pérez",
  "email": "juan.perez@colegio.cl",
  "rol_nombre": "Docente",
  "activo": true
}
```

#### Cambiar contraseña
```http
POST /api/v1/auth/change-password/
Authorization: Token {tu_token}
Content-Type: application/json

{
  "current_password": "contraseña_actual",
  "new_password": "nueva_contraseña",
  "confirm_password": "nueva_contraseña"
}
```

**Respuesta exitosa:**
```json
{
  "message": "Contraseña actualizada exitosamente",
  "token": "nuevo_token_generado_aqui"
}
```

**Errores posibles:**
- `400`: Campos faltantes, contraseñas no coinciden, o contraseña muy corta (mínimo 6 caracteres)
- `401`: Contraseña actual incorrecta

**Nota importante:** 
- Al cambiar la contraseña, se genera un **nuevo token**. 
- Debes guardar y usar este nuevo token en las siguientes peticiones.
- El token anterior queda invalidado por seguridad.

---

### **Tickets**

#### Listar tickets del usuario
```http
GET /api/v1/tickets/
Authorization: Token {tu_token}
```

**Filtrado automático por rol:**
- **Docente**: Solo ve sus propios tickets
- **TI**: Ve tickets asignados a él
- **Admin/Superadmin**: Ve todos los tickets

**Respuesta:**
```json
{
  "count": 15,
  "next": "http://api.example.com/api/v1/tickets/?page=2",
  "previous": null,
  "results": [
    {
      "ticket_id": 1,
      "titulo": "Proyector no funciona",
      "estado": "ABIERTO",
      "estado_display": "Abierto",
      "usuario_creador_nombre": "Juan Pérez",
      "categoria_nombre": "Hardware",
      "prioridad_nivel": "Alta",
      "fecha_creacion": "2025-11-20T10:30:00Z",
      "fijado": false
    }
  ]
}
```

#### Crear nuevo ticket (solo Docente)
```http
POST /api/v1/tickets/
Authorization: Token {tu_token}
Content-Type: application/json

{
  "titulo": "Problema con proyector",
  "descripcion": "El proyector de la sala 201 no enciende",
  "categoria": 1,
  "prioridad": 2
}
```

**Respuesta:**
```json
{
  "ticket_id": 123,
  "titulo": "Problema con proyector",
  "descripcion": "El proyector de la sala 201 no enciende",
  "estado": "ABIERTO",
  "estado_display": "Abierto",
  "usuario_creador": {
    "rut": 12345678,
    "nombre": "Juan Pérez",
    "email": "juan.perez@colegio.cl",
    "rol_nombre": "Docente"
  },
  "categoria": {
    "categoria_id": 1,
    "nombre": "Hardware",
    "descripcion": "Problemas de hardware"
  },
  "prioridad": {
    "prioridad_id": 2,
    "Tipo_Nivel": "Alta",
    "sla_horas": 4
  },
  "fecha_creacion": "2025-11-25T14:30:00Z",
  "fecha_resolucion": null,
  "fijado": false,
  "comentarios": []
}
```

#### Obtener detalle de un ticket
```http
GET /api/v1/tickets/{ticket_id}/
Authorization: Token {tu_token}
```

**Respuesta:** Igual a la respuesta de crear ticket, pero incluye comentarios.

#### Añadir comentario a un ticket
```http
POST /api/v1/tickets/{ticket_id}/add_comment/
Authorization: Token {tu_token}
Content-Type: application/json

{
  "contenido": "El problema persiste después de reiniciar"
}
```

**Respuesta:**
```json
{
  "comentario_id": 45,
  "contenido": "El problema persiste después de reiniciar",
  "autor_nombre": "Juan Pérez",
  "autor_rol": "Docente",
  "fecha_creacion": "2025-11-25T15:00:00Z"
}
```

#### Fijar/Desfijar ticket (solo TI)
```http
POST /api/v1/tickets/{ticket_id}/toggle_pin/
Authorization: Token {tu_token}
```

**Respuesta:**
```json
{
  "ticket_id": 123,
  "fijado": true
}
```

---

### **Notificaciones**

#### Listar notificaciones del usuario
```http
GET /api/v1/notificaciones/
Authorization: Token {tu_token}
```

**Respuesta:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "notificacion_id": 1,
      "mensaje": "Tu ticket 'Proyector no funciona' ha sido asignado a TI",
      "leido": false,
      "fecha_creacion": "2025-11-25T10:00:00Z",
      "ticket_id": 123,
      "ticket_titulo": "Proyector no funciona"
    }
  ]
}
```

#### Marcar notificación como leída
```http
POST /api/v1/notificaciones/{notificacion_id}/mark_read/
Authorization: Token {tu_token}
```

**Respuesta:**
```json
{
  "status": "notificación marcada como leída"
}
```

#### Marcar todas las notificaciones como leídas
```http
POST /api/v1/notificaciones/mark_all_read/
Authorization: Token {tu_token}
```

**Respuesta:**
```json
{
  "status": "5 notificaciones marcadas como leídas"
}
```

---

### **Estadísticas**

#### Obtener estadísticas del usuario
```http
GET /api/v1/stats/
Authorization: Token {tu_token}
```

**Respuesta (Docente):**
```json
{
  "total_tickets": 10,
  "abiertos": 3,
  "en_progreso": 2,
  "resueltos": 4,
  "cerrados": 1
}
```

**Respuesta (TI):**
```json
{
  "total_tickets": 15,
  "abiertos": 5,
  "en_progreso": 7,
  "resueltos": 2,
  "cerrados": 1,
  "fijados": 3
}
```

---

### **Datos Auxiliares**

#### Listar categorías disponibles
```http
GET /api/v1/categorias/
Authorization: Token {tu_token}
```

**Respuesta:**
```json
[
  {
    "categoria_id": 1,
    "nombre": "Hardware",
    "descripcion": "Problemas de hardware"
  },
  {
    "categoria_id": 2,
    "nombre": "Software",
    "descripcion": "Problemas de software"
  }
]
```

#### Listar prioridades disponibles
```http
GET /api/v1/prioridades/
Authorization: Token {tu_token}
```

**Respuesta:**
```json
[
  {
    "prioridad_id": 1,
    "Tipo_Nivel": "Baja",
    "sla_horas": 48
  },
  {
    "prioridad_id": 2,
    "Tipo_Nivel": "Media",
    "sla_horas": 24
  },
  {
    "prioridad_id": 3,
    "Tipo_Nivel": "Alta",
    "sla_horas": 4
  },
  {
    "prioridad_id": 4,
    "Tipo_Nivel": "Crítica",
    "sla_horas": 1
  }
]
```

---

## Estados de Tickets

Los tickets pueden tener los siguientes estados:

| Estado | Descripción |
|--------|-------------|
| `ABIERTO` | Ticket recién creado, esperando asignación |
| `EN_PROGRESO` | Ticket asignado y en proceso de resolución |
| `RESUELTO` | Problema resuelto, pendiente de verificación |
| `CERRADO` | Ticket completado y cerrado |

---

## Códigos de Error

| Código | Significado |
|--------|-------------|
| `200` | OK - Operación exitosa |
| `201` | Created - Recurso creado exitosamente |
| `400` | Bad Request - Datos inválidos |
| `401` | Unauthorized - Token inválido o ausente |
| `403` | Forbidden - Sin permisos |
| `404` | Not Found - Recurso no encontrado |
| `500` | Internal Server Error - Error del servidor |

---

## Ejemplo de flujo completo (Flutter/React Native)

### 1. Login
```dart
// Flutter example
final response = await http.post(
  Uri.parse('http://ticketeraprime.com/api/v1/auth/login/'),
  headers: {'Content-Type': 'application/json'},
  body: json.encode({
    'email': 'docente@colegio.cl',
    'password': 'mi_password'
  }),
);
final data = json.decode(response.body);
final token = data['token'];
```

### 2. Listar mis tickets
```dart
final response = await http.get(
  Uri.parse('http://ticketeraprime.com/api/v1/tickets/'),
  headers: {
    'Authorization': 'Token $token',
  },
);
final tickets = json.decode(response.body)['results'];
```

### 3. Crear nuevo ticket
```dart
final response = await http.post(
  Uri.parse('http://ticketeraprime.com/api/v1/tickets/'),
  headers: {
    'Authorization': 'Token $token',
    'Content-Type': 'application/json',
  },
  body: json.encode({
    'titulo': 'Problema con proyector',
    'descripcion': 'No enciende',
    'categoria': 1,
    'prioridad': 2,
  }),
);
```

### 4. Añadir comentario
```dart
final response = await http.post(
  Uri.parse('http://ticketeraprime.com/api/v1/tickets/123/add_comment/'),
  headers: {
    'Authorization': 'Token $token',
    'Content-Type': 'application/json',
  },
  body: json.encode({
    'contenido': 'Ya revisé el cable de poder',
  }),
);
```

---

## Testing con cURL

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "docente@colegio.cl", "password": "123456"}'
```

### Listar tickets
```bash
curl -X GET http://localhost:8000/api/v1/tickets/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

### Crear ticket
```bash
curl -X POST http://localhost:8000/api/v1/tickets/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Problema con proyector",
    "descripcion": "No enciende",
    "categoria": 1,
    "prioridad": 2
  }'
```

---

## Notas Importantes

1. **Todos los endpoints requieren autenticación** excepto `/api/v1/auth/login/`
2. **Los tokens no expiran** (puedes implementar refresh tokens con `djangorestframework-simplejwt` si lo necesitas)
3. **La paginación está configurada a 20 items por página**
4. **Las fechas están en formato ISO 8601 (UTC)**
5. **Solo los Docentes pueden crear tickets desde la app móvil**
6. **Solo los técnicos TI pueden fijar tickets**

---

## Configuración del Servidor

El servidor debe estar configurado con:

- **DEBUG**: False (en producción)
- **ALLOWED_HOSTS**: Incluir el dominio de tu servidor
- **CORS**: Configurar si la app móvil accede desde dominio diferente
- **HTTPS**: Altamente recomendado para proteger los tokens

---

## Próximos Pasos

Ahora puedes desarrollar la aplicación móvil con:

- **Flutter** (recomendado para iOS + Android)
- **React Native** (si prefieres JavaScript)
- **Kotlin/Swift** (nativo)

La API está lista y funcionando. Solo necesitas consumirla desde tu app móvil.
