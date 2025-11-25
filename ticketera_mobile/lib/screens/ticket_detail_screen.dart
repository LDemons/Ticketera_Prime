import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'package:intl/intl.dart';

class TicketDetailScreen extends StatefulWidget {
  final int ticketId;

  const TicketDetailScreen({super.key, required this.ticketId});

  @override
  State<TicketDetailScreen> createState() => _TicketDetailScreenState();
}

class _TicketDetailScreenState extends State<TicketDetailScreen> {
  final _apiService = ApiService();
  final _comentarioController = TextEditingController();
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
          backgroundColor: Color(0xFF2fb171),
        ),
      );

      _comentarioController.clear();
      _loadTicketDetail();
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: ${e.toString().replaceAll('Exception: ', '')}'),
          backgroundColor: const Color(0xFFea5573),
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

  Color _getEstadoColor(String estado) {
    switch (estado) {
      case 'ABIERTO':
        return const Color(0xFF2196F3);
      case 'EN_PROGRESO':
        return const Color(0xFFFFA726);
      case 'RESUELTO':
        return const Color(0xFF2fb171);
      case 'CERRADO':
        return const Color(0xFF6b6b7a);
      default:
        return const Color(0xFF6b6b7a);
    }
  }

  Color _getPrioridadColor(String prioridad) {
    switch (prioridad.toUpperCase()) {
      case 'BAJO':
        return const Color(0xFF2fb171); // Verde
      case 'MEDIO':
        return const Color(0xFFFFA726); // Amarillo/Naranja
      case 'ALTO':
        return const Color(0xFFea5573); // Rojo
      default:
        return const Color(0xFF6b6b7a); // Gris
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
      appBar: AppBar(
            title: Text(_ticket != null ? 'Ticket #T${_ticket!['ticket_id']}' : 'Cargando...'),
            actions: [
                IconButton(
                icon: const Icon(Icons.logout),
                onPressed: () async {
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
                            backgroundColor: const Color(0xFFea5573),
                            ),
                            child: const Text('Cerrar Sesión'),
                        ),
                        ],
                    ),
                    );

                    if (confirm == true && mounted) {
                    await _apiService.logout();
                    if (!mounted) return;
                    Navigator.of(context).pushNamedAndRemoveUntil('/', (route) => false);
                    }
                },
                tooltip: 'Cerrar Sesión',
                ),
            ],
        ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.error_outline, size: 64, color: Color(0xFFea5573)),
                      const SizedBox(height: 16),
                      Text('Error', style: Theme.of(context).textTheme.titleLarge),
                      const SizedBox(height: 8),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 32),
                        child: Text(
                          _errorMessage!,
                          textAlign: TextAlign.center,
                          style: const TextStyle(color: Color(0xFF6b6b7a)),
                        ),
                      ),
                      const SizedBox(height: 24),
                      ElevatedButton(
                        onPressed: _loadTicketDetail,
                        child: const Text('Reintentar'),
                      ),
                    ],
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Estado
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        decoration: BoxDecoration(
                          color: _getEstadoColor(_ticket!['estado']),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          _ticket!['estado'].replaceAll('_', ' '),
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Título
                      Text(
                        _ticket!['titulo'],
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: const Color(0xFF2a0441),
                            ),
                      ),
                      const SizedBox(height: 8),

                      // Fecha
                      Text(
                        'Creado: ${_formatFecha(_ticket!['fecha_creacion'])}',
                        style: const TextStyle(color: Color(0xFF6b6b7a)),
                      ),
                      const SizedBox(height: 24),

                      // Descripción
                      const Text(
                        'Descripción:',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _ticket!['descripcion'],
                        style: const TextStyle(fontSize: 15),
                      ),
                      const SizedBox(height: 24),

                      // Información adicional con colores
                      Row(
                        children: [
                          Expanded(
                            child: Card(
                              color: Colors.white,
                              child: Padding(
                                padding: const EdgeInsets.all(12),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text(
                                      'Categoría',
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: Color(0xFF6b6b7a),
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      _ticket!['categoria']?['nombre'] ?? 'N/A',
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 14,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Card(
                                color: Colors.white,
                              child: Padding(
                                padding: const EdgeInsets.all(12),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text(
                                      'Prioridad',
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: Color(0xFF6b6b7a),
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      _ticket!['prioridad']?['Tipo_Nivel'] ?? 'N/A',
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 14,
                                        color: _getPrioridadColor(_ticket!['prioridad']?['Tipo_Nivel'] ?? ''),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 32),

                      // Comentarios
                      const Text(
                        'Comentarios:',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 12),

                      if (_ticket!['comentarios'] == null || _ticket!['comentarios'].isEmpty)
                        const Center(
                          child: Padding(
                            padding: EdgeInsets.all(24),
                            child: Text(
                              'Aún no hay respuestas del equipo técnico',
                              style: TextStyle(color: Color(0xFF6b6b7a)),
                            ),
                          ),
                        )
                      else
                        ..._ticket!['comentarios'].map<Widget>((comentario) {
                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      CircleAvatar(
                                        backgroundColor: const Color(0xFF2a0441),
                                        radius: 16,
                                        child: Text(
                                          (comentario['autor']?['nombre'] ?? 'U')[0].toUpperCase(),
                                          style: const TextStyle(
                                            color: Colors.white,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ),
                                      const SizedBox(width: 12),
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              comentario['autor']?['nombre'] ?? 'Usuario',
                                              style: const TextStyle(
                                                fontWeight: FontWeight.bold,
                                              ),
                                            ),
                                            Text(
                                              _formatFecha(comentario['fecha_creacion']),
                                              style: const TextStyle(
                                                fontSize: 12,
                                                color: Color(0xFF6b6b7a),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 12),
                                  Text(comentario['contenido'] ?? ''),
                                ],
                              ),
                            ),
                          );
                        }).toList(),

                      const SizedBox(height: 24),

                      // Agregar comentario
                      const Text(
                        'Agregar seguimiento:',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _comentarioController,
                        maxLines: 3,
                        decoration: const InputDecoration(
                          hintText: 'Escribe tu comentario aquí...',
                        ),
                      ),
                      const SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          onPressed: _isSubmitting ? null : _addComment,
                          icon: _isSubmitting
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                  ),
                                )
                              : const Icon(Icons.send),
                          label: Text(_isSubmitting ? 'Enviando...' : 'Enviar Comentario'),
                        ),
                      ),
                    ],
                  ),
                ),
    );
  }
}