import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../utils/app_colors.dart';
import '../widgets/common_widgets.dart';
import 'package:intl/intl.dart';
import 'login_screen.dart';

class TicketDetailScreen extends StatefulWidget {
  final int ticketId;

  const TicketDetailScreen({super.key, required this.ticketId});

  @override
  State<TicketDetailScreen> createState() => _TicketDetailScreenState();
}

class _TicketDetailScreenState extends State<TicketDetailScreen> {
  final _apiService = ApiService();
  final _comentarioController = TextEditingController();
  final _scrollController = ScrollController();
  Map<String, dynamic>? _ticket;
  bool _isLoading = true;
  bool _isSubmitting = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadTicketDetail();
  }

  @override
  void dispose() {
    _comentarioController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _loadTicketDetail() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final ticket = await _apiService.getTicketDetail(widget.ticketId);
      if (mounted) {
        setState(() {
          _ticket = ticket;
          _isLoading = false;
        });
        // Auto-scroll al final después de cargar
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (_scrollController.hasClients) {
            _scrollController.animateTo(
              _scrollController.position.maxScrollExtent,
              duration: const Duration(milliseconds: 300),
              curve: Curves.easeOut,
            );
          }
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

  Future<void> _addComment() async {
    if (_comentarioController.text.trim().isEmpty) {
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      await _apiService.addComment(
        widget.ticketId,
        _comentarioController.text.trim(),
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✓ Comentario agregado'),
          backgroundColor: AppColors.green,
          duration: Duration(seconds: 2),
        ),
      );

      _comentarioController.clear();
      await _loadTicketDetail();
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: ${e.toString().replaceAll('Exception: ', '')}'),
          backgroundColor: AppColors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
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
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.red),
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

  String _formatFecha(String? fecha) {
    if (fecha == null) return '';
    try {
      final date = DateTime.parse(fecha);
      return DateFormat('dd/MM/yyyy HH:mm').format(date);
    } catch (e) {
      return fecha;
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
        title: Text(_ticket != null ? 'Ticket #T${_ticket!['ticket_id'].toString().padLeft(3, '0')}' : 'Cargando...'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_outlined),
            onPressed: _loadTicketDetail,
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
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 32),
                        child: Text(
                          _errorMessage!,
                          textAlign: TextAlign.center,
                          style: const TextStyle(color: AppColors.muted),
                        ),
                      ),
                      const SizedBox(height: 24),
                      ElevatedButton.icon(
                        onPressed: _loadTicketDetail,
                        icon: const Icon(Icons.refresh),
                        label: const Text('Reintentar'),
                      ),
                    ],
                  ),
                )
              : Column(
                  children: [
                    // Header del ticket
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        border: Border(
                          bottom: BorderSide(color: AppColors.line),
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              UserAvatar(
                                nombre: _ticket!['usuario_creador']?['nombre'] ?? 'Usuario',
                                size: 40,
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      _ticket!['titulo'],
                                      style: const TextStyle(
                                        fontSize: 17,
                                        fontWeight: FontWeight.w700,
                                        color: AppColors.text,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      'Creado: ${_formatFecha(_ticket!['fecha_creacion'])}',
                                      style: const TextStyle(
                                        fontSize: 13,
                                        color: AppColors.muted,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: [
                              StatusTag(
                                estado: _ticket!['estado'],
                                label: _ticket!['estado_display'],
                              ),
                              if (_ticket!['categoria']?['nombre'] != null)
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: AppColors.blue100,
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    _ticket!['categoria']['nombre'],
                                    style: const TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.w600,
                                      color: AppColors.blue,
                                    ),
                                  ),
                                ),
                              if (_ticket!['prioridad']?['Tipo_Nivel'] != null)
                                PriorityTag(
                                  prioridad: _ticket!['prioridad']['Tipo_Nivel'],
                                ),
                            ],
                          ),
                        ],
                      ),
                    ),

                    // Cuerpo con comentarios
                    Expanded(
                      child: ListView(
                        controller: _scrollController,
                        padding: const EdgeInsets.all(16),
                        children: [
                          // Descripción original como bubble
                          _CommentBubble(
                            autor: _ticket!['usuario_creador']?['nombre'] ?? 'Usuario',
                            autorRol: _ticket!['usuario_creador']?['rol'] ?? 'Docente',
                            contenido: _ticket!['descripcion'],
                            fecha: _ticket!['fecha_creacion'],
                            isOriginal: true,
                          ),
                          const SizedBox(height: 12),

                          // Comentarios
                          if (_ticket!['comentarios'] == null || _ticket!['comentarios'].isEmpty)
                            Container(
                              padding: const EdgeInsets.all(20),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                border: Border.all(color: AppColors.line),
                                borderRadius: BorderRadius.circular(14),
                              ),
                              child: const Center(
                                child: Text(
                                  'Aún no hay respuestas del equipo de TI',
                                  style: TextStyle(color: AppColors.muted),
                                  textAlign: TextAlign.center,
                                ),
                              ),
                            )
                          else
                            ..._ticket!['comentarios'].map<Widget>((comentario) {
                              return Padding(
                                padding: const EdgeInsets.only(bottom: 12),
                                child: _CommentBubble(
                                  autor: comentario['autor_nombre'] ?? 'Usuario',
                                  autorRol: comentario['autor_rol'] ?? 'Usuario',
                                  contenido: comentario['contenido'] ?? '',
                                  fecha: comentario['fecha_creacion'],
                                  isOriginal: false,
                                ),
                              );
                            }).toList(),
                        ],
                      ),
                    ),

                    // Composer fijo en la parte inferior
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        border: Border(
                          top: BorderSide(color: AppColors.line),
                        ),
                      ),
                      padding: const EdgeInsets.all(16),
                      child: SafeArea(
                        child: Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: _comentarioController,
                                maxLines: null,
                                textInputAction: TextInputAction.newline,
                                decoration: InputDecoration(
                                  hintText: 'Escribe una respuesta o seguimiento...',
                                  hintStyle: const TextStyle(color: AppColors.muted),
                                  filled: true,
                                  fillColor: AppColors.bg,
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(10),
                                    borderSide: const BorderSide(color: AppColors.line),
                                  ),
                                  enabledBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(10),
                                    borderSide: const BorderSide(color: AppColors.line),
                                  ),
                                  focusedBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(10),
                                    borderSide: const BorderSide(color: AppColors.indigo800, width: 2),
                                  ),
                                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Material(
                              color: AppColors.indigo800,
                              borderRadius: BorderRadius.circular(10),
                              child: InkWell(
                                borderRadius: BorderRadius.circular(10),
                                onTap: _isSubmitting ? null : _addComment,
                                child: Container(
                                  width: 48,
                                  height: 48,
                                  padding: const EdgeInsets.all(12),
                                  child: _isSubmitting
                                      ? const SizedBox(
                                          width: 20,
                                          height: 20,
                                          child: CircularProgressIndicator(
                                            strokeWidth: 2,
                                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                          ),
                                        )
                                      : const Icon(
                                          Icons.send,
                                          color: Colors.white,
                                          size: 20,
                                        ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
    );
  }
}

class _CommentBubble extends StatelessWidget {
  final String autor;
  final String autorRol;
  final String contenido;
  final String? fecha;
  final bool isOriginal;

  const _CommentBubble({
    required this.autor,
    required this.autorRol,
    required this.contenido,
    this.fecha,
    this.isOriginal = false,
  });

  String _formatFecha(String? fecha) {
    if (fecha == null) return '';
    try {
      final date = DateTime.parse(fecha);
      return DateFormat('dd/MM/yyyy HH:mm').format(date);
    } catch (e) {
      return fecha;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isTI = autorRol == 'TI';
    
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: isOriginal 
            ? Colors.white 
            : (isTI ? AppColors.blue100 : Colors.white),
        border: Border.all(color: AppColors.line),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              UserAvatar(nombre: autor, size: 32),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          autor,
                          style: const TextStyle(
                            fontWeight: FontWeight.w700,
                            fontSize: 14,
                            color: AppColors.text,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          '($autorRol)',
                          style: const TextStyle(
                            fontSize: 12,
                            color: AppColors.muted,
                          ),
                        ),
                      ],
                    ),
                    if (fecha != null)
                      Text(
                        _formatFecha(fecha),
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppColors.muted,
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
          if (isOriginal) ...[
            const SizedBox(height: 8),
            const Text(
              'Descripción original:',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 13,
                color: AppColors.muted,
              ),
            ),
          ],
          const SizedBox(height: 10),
          Text(
            contenido,
            style: const TextStyle(
              fontSize: 15,
              height: 1.5,
              color: AppColors.text,
            ),
          ),
        ],
      ),
    );
  }
}
