import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../utils/app_colors.dart';
import '../widgets/common_widgets.dart';
import 'ticket_detail_screen.dart';
import 'create_ticket_screen.dart';
import 'notificaciones_screen.dart';
import 'login_screen.dart';

class TicketsListScreen extends StatefulWidget {
  const TicketsListScreen({super.key});

  @override
  State<TicketsListScreen> createState() => _TicketsListScreenState();
}

class _TicketsListScreenState extends State<TicketsListScreen> {
  final _apiService = ApiService();
  List<dynamic> _tickets = [];
  bool _isLoading = true;
  String? _errorMessage;
  int _unreadNotifications = 0;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    await Future.wait([
      _loadTickets(),
      _loadUnreadNotifications(),
    ]);
  }

  Future<void> _loadTickets() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final tickets = await _apiService.getTickets();
      if (mounted) {
        setState(() {
          _tickets = tickets;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString().replaceAll('Exception: ', '');
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _loadUnreadNotifications() async {
    try {
      final notificaciones = await _apiService.getNotificaciones();
      if (mounted) {
        setState(() {
          _unreadNotifications = notificaciones.where((n) => n['leido'] == false).length;
        });
      }
    } catch (e) {
      debugPrint('Error cargando notificaciones: $e');
    }
  }

  Future<void> _handleLogout() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cerrar Sesión'),
        content: const Text('¿Estás seguro que deseas cerrar sesión?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.red,
            ),
            child: const Text('Cerrar Sesión'),
          ),
        ],
      ),
    );

    if (confirm == true && mounted) {
      await _apiService.logout();
      if (!mounted) return;
      
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (context) => const LoginScreen()),
        (route) => false,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg,
      appBar: AppBar(
        backgroundColor: AppColors.indigo800,
        foregroundColor: Colors.white,
        elevation: 0,
        title: Row(
          children: [
            Icon(Icons.confirmation_number, size: 24),
            const SizedBox(width: 12),
            const Text('Ticketera Prime'),
          ],
        ),
        actions: [
          // Notificaciones con badge
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined),
                onPressed: () async {
                  await Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const NotificacionesScreen(),
                    ),
                  );
                  _loadUnreadNotifications();
                },
                tooltip: 'Notificaciones',
              ),
              if (_unreadNotifications > 0)
                Positioned(
                  right: 8,
                  top: 8,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                    decoration: BoxDecoration(
                      color: AppColors.red,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    constraints: const BoxConstraints(minWidth: 18, minHeight: 18),
                    child: Text(
                      _unreadNotifications > 99 ? '99+' : '$_unreadNotifications',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.refresh_outlined),
            onPressed: _loadData,
            tooltip: 'Actualizar',
          ),
          IconButton(
            icon: const Icon(Icons.logout_outlined),
            onPressed: _handleLogout,
            tooltip: 'Cerrar sesión',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(AppColors.indigo800),
              ),
            )
          : _errorMessage != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.error_outline, size: 60, color: AppColors.red),
                      const SizedBox(height: 16),
                      Text(
                        _errorMessage!,
                        style: const TextStyle(color: AppColors.muted),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 24),
                      ElevatedButton.icon(
                        onPressed: _loadData,
                        icon: const Icon(Icons.refresh),
                        label: const Text('Reintentar'),
                      ),
                    ],
                  ),
                )
              : _tickets.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.inbox_outlined, size: 60, color: AppColors.muted),
                          const SizedBox(height: 16),
                          const Text(
                            'No tienes tickets',
                            style: TextStyle(fontSize: 18, color: AppColors.muted),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'Crea tu primer ticket',
                            style: TextStyle(color: AppColors.muted),
                          ),
                        ],
                      ),
                    )
                  : RefreshIndicator(
                      color: AppColors.indigo800,
                      onRefresh: _loadData,
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _tickets.length,
                        itemBuilder: (context, index) {
                          final ticket = _tickets[index];
                          return _TicketCard(
                            ticket: ticket,
                            onTap: () async {
                              await Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => TicketDetailScreen(
                                    ticketId: ticket['ticket_id'],
                                  ),
                                ),
                              );
                              _loadData();
                            },
                          );
                        },
                      ),
                    ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          await Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const CreateTicketScreen(),
            ),
          );
          _loadData();
        },
        backgroundColor: AppColors.indigo800,
        icon: const Icon(Icons.add),
        label: const Text('Nuevo Ticket'),
      ),
    );
  }
}

class _TicketCard extends StatelessWidget {
  final Map<String, dynamic> ticket;
  final VoidCallback onTap;

  const _TicketCard({
    required this.ticket,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final nombreCreador = ticket['usuario_creador_nombre'] ?? 'Usuario';
    final titulo = ticket['titulo'] ?? 'Sin título';
    final ticketId = ticket['ticket_id'] ?? 0;
    final estado = ticket['estado'] ?? 'ABIERTO';
    final estadoDisplay = ticket['estado_display'] ?? estado;
    final fijado = ticket['fijado'] ?? false;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(
          color: fijado ? AppColors.blue : AppColors.line,
          width: fijado ? 2 : 1,
        ),
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              children: [
                // Avatar
                UserAvatar(nombre: nombreCreador, size: 44),
                const SizedBox(width: 12),
                // Contenido
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Título con pin
                      Row(
                        children: [
                          if (fijado) ...[
                            const Icon(
                              Icons.push_pin,
                              size: 16,
                              color: AppColors.blue,
                            ),
                            const SizedBox(width: 4),
                          ],
                          Expanded(
                            child: Text(
                              titulo,
                              style: const TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.w700,
                                color: AppColors.text,
                                height: 1.4,
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      // Meta info
                      Wrap(
                        spacing: 8,
                        runSpacing: 6,
                        crossAxisAlignment: WrapCrossAlignment.center,
                        children: [
                          Text(
                            '#T${ticketId.toString().padLeft(3, '0')}',
                            style: const TextStyle(
                              color: AppColors.muted,
                              fontSize: 13,
                            ),
                          ),
                          StatusTag(estado: estado, label: estadoDisplay),
                        ],
                      ),
                    ],
                  ),
                ),
                // Icono flecha
                const Icon(
                  Icons.chevron_right,
                  color: AppColors.muted,
                  size: 24,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
