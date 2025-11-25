import 'package:flutter/material.dart';

/// Colores de la aplicación - Basados en estilos.css de la web
class AppColors {
  // Colores principales
  static const indigo800 = Color(0xFF2a0441);  // Sidebar
  static const lavender = Color(0xFFb9a7d3);    // Acento
  static const bg = Color(0xFFf4f6fb);          // Fondo
  static const card = Color(0xFFffffff);        // Tarjetas
  static const line = Color(0xFFe7e8ee);        // Líneas
  static const text = Color(0xFF1f2430);        // Texto
  static const muted = Color(0xFF6b6b7a);       // Texto secundario
  
  // Colores de estado
  static const blue = Color(0xFF2f73d9);
  static const blue100 = Color(0xFFeaf1ff);
  static const green = Color(0xFF2fb171);
  static const red = Color(0xFFea5573);
  static const orange = Color(0xFFff9c5b);
  
  // Tags de estado de tickets
  static const tagOpenBg = Color(0xFFe3f2fd);
  static const tagOpenText = Color(0xFF1976d2);
  static const tagOpenBorder = Color(0xFF90caf9);
  
  static const tagProgressBg = Color(0xFFfff7e7);
  static const tagProgressText = Color(0xFF8a5a12);
  static const tagProgressBorder = Color(0xFFffe6b8);
  
  static const tagResolvedBg = Color(0xFFe8f5e9);
  static const tagResolvedText = Color(0xFF388e3c);
  static const tagResolvedBorder = Color(0xFFa5d6a7);
  
  static const tagClosedBg = Color(0xFFf5f5f5);
  static const tagClosedText = Color(0xFF616161);
  static const tagClosedBorder = Color(0xFFbdbdbd);
  
  static const tagRejectedBg = Color(0xFFffebee);
  static const tagRejectedText = Color(0xFFc62828);
  static const tagRejectedBorder = Color(0xFFef9a9a);
  
  // Tags de prioridad
  static const tagHighBg = Color(0xFFffebee);
  static const tagHighText = Color(0xFFc62828);
  static const tagHighBorder = Color(0xFFef9a9a);
  
  static const tagMediumBg = Color(0xFFfff7e7);
  static const tagMediumText = Color(0xFF8a5a12);
  static const tagMediumBorder = Color(0xFFffe6b8);
  
  static const tagLowBg = Color(0xFFe8f5e9);
  static const tagLowText = Color(0xFF388e3c);
  static const tagLowBorder = Color(0xFFa5d6a7);
}

/// Helpers para generar colores de avatar basados en el nombre
class AvatarColors {
  static Color fromName(String name) {
    if (name.isEmpty) return AppColors.indigo800;
    
    // Lista de colores para avatares
    final colors = [
      const Color(0xFF4aa3d7),
      const Color(0xFF58b676),
      const Color(0xFFd58f44),
      const Color(0xFFc35656),
      const Color(0xFFc06bcf),
      AppColors.indigo800,
      AppColors.blue,
      AppColors.green,
      AppColors.orange,
      AppColors.red,
    ];
    
    // Seleccionar color basado en la primera letra
    final index = name.toUpperCase().codeUnitAt(0) % colors.length;
    return colors[index];
  }
}
