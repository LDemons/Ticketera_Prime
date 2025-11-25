class Notificacion {
  final int notificacionId;
  final String tipo;
  final String mensaje;
  final bool leida;
  final DateTime fechaCreacion;
  final int? ticketId;
  final String? ticketTitulo;

  Notificacion({
    required this.notificacionId,
    required this.tipo,
    required this.mensaje,
    required this.leida,
    required this.fechaCreacion,
    this.ticketId,
    this.ticketTitulo,
  });

  factory Notificacion.fromJson(Map<String, dynamic> json) {
    return Notificacion(
      notificacionId: json['notificacion_id'] ?? 0,
      tipo: json['tipo'] ?? 'GENERAL',
      mensaje: json['mensaje'] ?? 'Sin mensaje',
      leida: json['leida'] ?? false,
      fechaCreacion: json['fecha_creacion'] != null 
          ? DateTime.parse(json['fecha_creacion'])
          : DateTime.now(),
      ticketId: json['ticket_id'],
      ticketTitulo: json['ticket_titulo'],
    );
  }
}
