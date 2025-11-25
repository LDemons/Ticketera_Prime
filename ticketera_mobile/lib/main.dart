import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'screens/create_ticket_screen.dart';
import 'services/api_service.dart';
import 'screens/tickets_list_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Ticketera Prime - Docentes',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primaryColor: const Color(0xFF2a0441),
        scaffoldBackgroundColor: const Color(0xFFF4F6FB),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2a0441),
          primary: const Color(0xFF2a0441),
          secondary: const Color(0xFFb9a7d3),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF2a0441),
          foregroundColor: Colors.white,
          elevation: 0,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF2a0441),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: const BorderSide(color: Color(0xFFe7e8ee)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: const BorderSide(color: Color(0xFFe7e8ee)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: const BorderSide(color: Color(0xFF2a0441), width: 2),
          ),
        ),
      ),
      home: const AuthCheck(),
    );
  }
}

class AuthCheck extends StatelessWidget {
  const AuthCheck({super.key});

  @override
  Widget build(BuildContext context) {
    final apiService = ApiService();
    
    return FutureBuilder<bool>(
      future: apiService.isAuthenticated(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            backgroundColor: Color(0xFF2a0441),
            body: Center(
              child: CircularProgressIndicator(color: Colors.white),
            ),
          );
        }
        
        if (snapshot.hasData && snapshot.data == true) {
          return const TicketsListScreen();
        }
        
        return const LoginScreen();
      },
    );
  }
}
