
  // MÃtodos con nombres en espaÃol (alias)
  Future<List<dynamic>> getNotificaciones() => getNotificaciones();
  
  Future<void> marcarNotificacionLeida(int notificacionId) => markNotificationAsRead(notificacionId);
  
  Future<void> marcarTodasNotificacionesLeidas() => markAllNotificationsAsRead();

  void setToken(String token) async {
    await _saveToken(token);
  }
