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
      notificacionId: json['notificacion_id'],
      tipo: json['tipo'],
      mensaje: json['mensaje'],
      leida: json['leida'],
      fechaCreacion: DateTime.parse(json['fecha_creacion']),
      ticketId: json['ticket_id'],
      ticketTitulo: json['ticket_titulo'],
    );
  }
}
