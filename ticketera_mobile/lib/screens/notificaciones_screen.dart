import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../models/notificacion.dart';
import 'ticket_detail_screen.dart';
import 'package:intl/intl.dart';

class NotificacionesScreen extends StatefulWidget {
  const NotificacionesScreen({super.key});

  @'State<NotificacionesScreen> createState() => _NotificacionesScreenState();
}

class _NotificacionesScreenState extends State<NotificacionesScreen> {
  final ApiService _apiService = ApiService();
  List<Notificacion> _notificaciones = [];
  bool _isLoading = true;
  int _unreadCount = 0;

  @'override
  void initState() {
    super.initState();
    _loadNotificaciones();
  }

  Future<void> _loadNotificaciones() async {
    setState(() => _isLoading = true);
    
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');
      
      if (token != null) {
        _apiService.setToken(token);
        final notificaciones = await _apiService.getNotificaciones();
        
        setState(() {
          _notificaciones = notificaciones;
          _unreadCount = notificaciones.where((n) => !n.leida).length;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  Future<void> _marcarComoLeida(int notificacionId) async {
    try {
      await _apiService.marcarNotificacionLeida(notificacionId);
      await _loadNotificaciones();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al marcar como leída: $e')),
        );
      }
    }
  }

  Future<void> _marcarTodasLeidas() async {
    try {
      await _apiService.marcarTodasNotificacionesLeidas();
      await _loadNotificaciones();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Todas las notificaciones marcadas como leídas')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  IconData _getIconByTipo(String tipo) {
    switch (tipo) {
      case 'ASIGNACION':
        return Icons.assignment_ind;
      case 'COMENTARIO':
        return Icons.comment;
      case 'CAMBIO_ESTADO':
        return Icons.update;
      case 'PRIORIDAD':
        return Icons.priority_high;
      default:
        return Icons.notifications;
    }
  }

  Color _getColorByTipo(String tipo) {
    switch (tipo) {
      case 'ASIGNACION':
        return Colors.blue;
      case 'COMENTARIO':
        return Colors.green;
      case 'CAMBIO_ESTADO':
        return Colors.orange;
      case 'PRIORIDAD':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  @'override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Notificaciones ($_unreadCount)'),
        backgroundColor: const Color(0xFF2a0441),
        actions: [
          if (_unreadCount > 0)
            IconButton(
              icon: const Icon(Icons.done_all),
              tooltip: 'Marcar todas como leídas',
              onPressed: _marcarTodasLeidas,
            ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              final shouldLogout = await showDialog<bool>(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('Cerrar sesión'),
                  content: const Text('¿Estás seguro de que deseas cerrar sesión?'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context, false),
                      child: const Text('Cancelar'),
                    ),
                    TextButton(
                      onPressed: () => Navigator.pop(context, true),
                      child: const Text('Cerrar sesión'),
                    ),
                  ],
                ),
              );

              if (shouldLogout == true) {
                final prefs = await SharedPreferences.getInstance();
                await prefs.remove('auth_token');
                if (mounted) {
                  Navigator.pushReplacementNamed(context, '/login');
                }
              }
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _notificaciones.isEmpty
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.notifications_none, size: 80, color: Colors.grey),
                      SizedBox(height: 16),
                      Text(
                        'No tienes notificaciones',
                        style: TextStyle(fontSize: 18, color: Colors.grey),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadNotificaciones,
                  child: ListView.builder(
                    itemCount: _notificaciones.length,
                    itemBuilder: (context, index) {
                      final notif = _notificaciones[index];
                      return Card(
                        margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        color: notif.leida ? Colors.white : Colors.blue.shade50,
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: _getColorByTipo(notif.tipo),
                            child: Icon(
                              _getIconByTipo(notif.tipo),
                              color: Colors.white,
                            ),
                          ),
                          title: Text(
                            notif.mensaje,
                            style: TextStyle(
                              fontWeight: notif.leida ? FontWeight.normal : FontWeight.bold,
                            ),
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              if (notif.ticketTitulo != null)
                                Text('Ticket: ${notif.ticketTitulo}'),
                              Text(
                                DateFormat('dd/MM/yyyy HH:mm').format(notif.fechaCreacion),
                                style: const TextStyle(fontSize: 12),
                              ),
                            ],
                          ),
                          trailing: !notif.leida
                              ? IconButton(
                                  icon: const Icon(Icons.check_circle_outline),
                                  onPressed: () => _marcarComoLeida(notif.notificacionId),
                                  tooltip: 'Marcar como leída',
                                )
                              : null,
                          onTap: () {
                            if (notif.ticketId != null) {
                              if (!notif.leida) {
                                _marcarComoLeida(notif.notificacionId);
                              }
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => TicketDetailScreen(
                                    ticketId: notif.ticketId!,
                                  ),
                                ),
                              );
                            } else if (!notif.leida) {
                              _marcarComoLeida(notif.notificacionId);
                            }
                          },
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
