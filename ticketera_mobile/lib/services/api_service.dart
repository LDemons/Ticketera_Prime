import 'dart:convert';
import '../models/notificacion.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // Lista de servidores a probar en orden de prioridad
  static const List<String> _serverUrls = [
    'https://ticketeraprime.com/api/v1',      // Producción
    'http://10.0.2.2:8000/api/v1',            // Emulador Android
  ];
  
  static String? _workingUrl;
  
  // Obtiene la URL del servidor que funciona
  static Future<String> _getWorkingUrl() async {
    // Si ya encontramos una URL que funciona, usarla
    if (_workingUrl != null) return _workingUrl!;
    
    // Probar cada servidor
    for (String url in _serverUrls) {
      try {
        final testResponse = await http.get(
          Uri.parse('${url.replaceAll('/api/v1', '')}/'),
        ).timeout(const Duration(seconds: 3));
        
        if (testResponse.statusCode < 500) {
          _workingUrl = url;
          print('✓ Servidor conectado: $url');
          return url;
        }
      } catch (e) {
        print('✗ Servidor no disponible: $url');
        continue;
      }
    }
    
    // Si ninguno funciona, usar el primero por defecto
    _workingUrl = _serverUrls[0];
    return _workingUrl!;
  }
  
  static String get baseUrl => _workingUrl ?? _serverUrls[0];
  
  // Helper para hacer requests con auto-detección de servidor
  Future<http.Response> _makeRequest(
    String endpoint,
    String method, {
    Map<String, String>? headers,
    Object? body,
  }) async {
    final url = await _getWorkingUrl();
    final uri = Uri.parse('$url$endpoint');
    final token = await getToken();
    
    final defaultHeaders = {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Token $token',
      ...?headers,
    };
    
    switch (method) {
      case 'GET':
        return await http.get(uri, headers: defaultHeaders).timeout(const Duration(seconds: 10));
      case 'POST':
        return await http.post(uri, headers: defaultHeaders, body: body).timeout(const Duration(seconds: 10));
      case 'PUT':
        return await http.put(uri, headers: defaultHeaders, body: body).timeout(const Duration(seconds: 10));
      case 'DELETE':
        return await http.delete(uri, headers: defaultHeaders).timeout(const Duration(seconds: 10));
      default:
        throw Exception('Método HTTP no soportado: $method');
    }
  }
  
  // ==========================================
  // AUTENTICACIÓN
  // ==========================================
  
  /// Login - Devuelve token y datos del usuario
  Future<Map<String, dynamic>> login(String email, String password) async {
    // Obtener servidor que funciona
    final url = await _getWorkingUrl();
    
    try {
      final response = await http.post(
        Uri.parse('$url/auth/login/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      ).timeout(const Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        // Guardar token localmente
        await _saveToken(data['token']);
        await _saveUserData(data['user']);
        return data;
      } else {
        throw Exception('Credenciales inválidas');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }
  
  /// Logout - Elimina token local
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    await prefs.remove('user_data');
  }
  
  /// Guardar token
  Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }
  
  /// Guardar datos del usuario
  Future<void> _saveUserData(Map<String, dynamic> user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('user_data', json.encode(user));
  }
  
  /// Obtener token guardado
  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('auth_token');
  }
  
  /// Obtener datos del usuario guardado
  Future<Map<String, dynamic>?> getUserData() async {
    final prefs = await SharedPreferences.getInstance();
    final userDataString = prefs.getString('user_data');
    if (userDataString != null) {
      return json.decode(userDataString);
    }
    return null;
  }
  
  /// Verificar si el usuario estÃ¡ autenticado
  Future<bool> isAuthenticated() async {
    final token = await getToken();
    return token != null;
  }
  
  // ==========================================
  // TICKETS
  // ==========================================
  
  /// Listar tickets del usuario (filtrado automático por rol)
  Future<List<dynamic>> getTickets() async {
    try {
      final response = await _makeRequest('/tickets/', 'GET');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['results'] ?? [];
      } else if (response.statusCode == 401) {
        throw Exception('Sesión expirada');
      } else {
        throw Exception('Error al cargar tickets');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }
  
  /// Obtener detalle de un ticket
  Future<Map<String, dynamic>> getTicketDetail(int ticketId) async {
    try {
      final response = await _makeRequest('/tickets/$ticketId/', 'GET');
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Error al cargar detalle del ticket');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }
  
  /// Crear nuevo ticket (solo para Docentes)
  Future<Map<String, dynamic>> createTicket({
    required String titulo,
    required String descripcion,
  }) async {
    try {
      final response = await _makeRequest(
        '/tickets/',
        'POST',
        body: json.encode({
          'titulo': titulo,
          'descripcion': descripcion,
        }),
      );
      
      if (response.statusCode == 201) {
        return json.decode(response.body);
      } else {
        final error = json.decode(response.body);
        throw Exception(error['error'] ?? 'Error al crear ticket');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }
  
  /// Añadir comentario a un ticket
  Future<Map<String, dynamic>> addComment(int ticketId, String contenido) async {
    try {
      final response = await _makeRequest(
        '/tickets/$ticketId/add_comment/',
        'POST',
        body: json.encode({'contenido': contenido}),
      );
      
      if (response.statusCode == 201) {
        return json.decode(response.body);
      } else {
        throw Exception('Error al añadir comentario');
      }
    } catch (e) {
      throw Exception('Error de conexiÃ³n: $e');
    }
  }
  
  /// Fijar/desfijar ticket (solo para TI)
  Future<Map<String, dynamic>> togglePinTicket(int ticketId) async {
    final token = await getToken();
    
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/tickets/$ticketId/toggle_pin/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Error al fijar ticket');
      }
    } catch (e) {
      throw Exception('Error de conexiÃ³n: $e');
    }
  }
  
  // ==========================================
  // NOTIFICACIONES
  // ==========================================
  
  /// Listar notificaciones del usuario
  Future<List<dynamic>> getNotificaciones() async {
    final token = await getToken();
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/notificaciones/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['results'] ?? [];
      } else {
        throw Exception('Error al cargar notificaciones');
      }
    } catch (e) {
      throw Exception('Error de conexiÃ³n: $e');
    }
  }
  
  /// Marcar notificaciÃ³n como leÃ­da
  Future<void> markNotificationAsRead(int notificacionId) async {
    final token = await getToken();
    
    try {
      await http.post(
        Uri.parse('$baseUrl/notificaciones/$notificacionId/mark_read/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json',
        },
      );
    } catch (e) {
      throw Exception('Error de conexiÃ³n: $e');
    }
  }
  
  /// Marcar todas las notificaciones como leÃ­das
  Future<void> markAllNotificationsAsRead() async {
    final token = await getToken();
    
    try {
      await http.post(
        Uri.parse('$baseUrl/notificaciones/mark_all_read/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json',
        },
      );
    } catch (e) {
      throw Exception('Error de conexiÃ³n: $e');
    }
  }

  // Métodos alias en español
  Future<void> marcarNotificacionLeida(int notificacionId) async {
    await markNotificationAsRead(notificacionId);
  }

  Future<void> marcarTodasNotificacionesLeidas() async {
    await markAllNotificationsAsRead();
  }

  void setToken(String token) async {
    await _saveToken(token);
  }
  
  // ==========================================
  // DATOS AUXILIARES
  // ==========================================
  
  /// Obtener lista de categorÃ­as
  Future<List<dynamic>> getCategorias() async {
    final token = await getToken();
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/categorias/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Error al cargar categorÃ­as');
      }
    } catch (e) {
      throw Exception('Error de conexiÃ³n: $e');
    }
  }
  
  /// Obtener lista de prioridades
  Future<List<dynamic>> getPrioridades() async {
    final token = await getToken();
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/prioridades/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Error al cargar prioridades');
      }
    } catch (e) {
      throw Exception('Error de conexiÃ³n: $e');
    }
  }
  
  /// Obtener estadÃ­sticas del usuario
  Future<Map<String, dynamic>> getStats() async {
    final token = await getToken();
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/stats/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Error al cargar estadÃ­sticas');
      }
    } catch (e) {
      throw Exception('Error de conexiÃ³n: $e');
    }
  }
  
  /// Obtener perfil del usuario
  Future<Map<String, dynamic>> getProfile() async {
    final token = await getToken();
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/auth/profile/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Error al cargar perfil');
      }
    } catch (e) {
      throw Exception('Error de conexiÃ³n: $e');
    }
  }
}

