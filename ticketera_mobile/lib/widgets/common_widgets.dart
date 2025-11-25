import 'package:flutter/material.dart';
import '../utils/app_colors.dart';

/// Tag/Badge para mostrar el estado de un ticket
class StatusTag extends StatelessWidget {
  final String estado;
  final String? label;

  const StatusTag({
    super.key,
    required this.estado,
    this.label,
  });

  @override
  Widget build(BuildContext context) {
    Color bg, text, border;
    String displayText = label ?? estado;

    switch (estado.toUpperCase()) {
      case 'ABIERTO':
        bg = AppColors.tagOpenBg;
        text = AppColors.tagOpenText;
        border = AppColors.tagOpenBorder;
        displayText = label ?? 'Abierto';
        break;
      case 'EN_PROGRESO':
        bg = AppColors.tagProgressBg;
        text = AppColors.tagProgressText;
        border = AppColors.tagProgressBorder;
        displayText = label ?? 'En Progreso';
        break;
      case 'RESUELTO':
        bg = AppColors.tagResolvedBg;
        text = AppColors.tagResolvedText;
        border = AppColors.tagResolvedBorder;
        displayText = label ?? 'Resuelto';
        break;
      case 'CERRADO':
        bg = AppColors.tagClosedBg;
        text = AppColors.tagClosedText;
        border = AppColors.tagClosedBorder;
        displayText = label ?? 'Cerrado';
        break;
      case 'RECHAZADO':
        bg = AppColors.tagRejectedBg;
        text = AppColors.tagRejectedText;
        border = AppColors.tagRejectedBorder;
        displayText = label ?? 'Rechazado';
        break;
      default:
        bg = AppColors.tagClosedBg;
        text = AppColors.tagClosedText;
        border = AppColors.tagClosedBorder;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        border: Border.all(color: border),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        displayText,
        style: TextStyle(
          color: text,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

/// Tag para mostrar prioridad
class PriorityTag extends StatelessWidget {
  final String prioridad;

  const PriorityTag({super.key, required this.prioridad});

  @override
  Widget build(BuildContext context) {
    Color bg, text, border;
    String displayText;

    switch (prioridad.toUpperCase()) {
      case 'ALTO':
      case 'HIGH':
        bg = AppColors.tagHighBg;
        text = AppColors.tagHighText;
        border = AppColors.tagHighBorder;
        displayText = 'Alta';
        break;
      case 'MEDIO':
      case 'MEDIUM':
        bg = AppColors.tagMediumBg;
        text = AppColors.tagMediumText;
        border = AppColors.tagMediumBorder;
        displayText = 'Media';
        break;
      case 'BAJO':
      case 'LOW':
        bg = AppColors.tagLowBg;
        text = AppColors.tagLowText;
        border = AppColors.tagLowBorder;
        displayText = 'Baja';
        break;
      default:
        bg = AppColors.tagMediumBg;
        text = AppColors.tagMediumText;
        border = AppColors.tagMediumBorder;
        displayText = prioridad;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        border: Border.all(color: border),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        displayText,
        style: TextStyle(
          color: text,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

/// Avatar circular con inicial del nombre
class UserAvatar extends StatelessWidget {
  final String nombre;
  final double size;

  const UserAvatar({
    super.key,
    required this.nombre,
    this.size = 44,
  });

  @override
  Widget build(BuildContext context) {
    final inicial = nombre.isNotEmpty ? nombre[0].toUpperCase() : '?';
    final color = AvatarColors.fromName(nombre);

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Center(
        child: Text(
          inicial,
          style: TextStyle(
            color: Colors.white,
            fontSize: size * 0.4,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    );
  }
}
