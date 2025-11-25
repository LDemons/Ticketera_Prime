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
        useMaterial3: true,
        primaryColor: const Color(0xFF2a0441),
        scaffoldBackgroundColor: const Color(0xFFF4F6FB),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2a0441),
          primary: const Color(0xFF2a0441),
          secondary: const Color(0xFFb9a7d3),
          surface: const Color(0xFFffffff),
          background: const Color(0xFFf4f6fb),
          error: const Color(0xFFea5573),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF2a0441),
          foregroundColor: Colors.white,
          elevation: 0,
          centerTitle: false,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF2a0441),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
            elevation: 0,
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: const BorderSide(color: Color(0xFFe7e8ee)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: const BorderSide(color: Color(0xFFe7e8ee)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: const BorderSide(color: Color(0xFF2a0441), width: 2),
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
        ),
        cardTheme: const CardThemeData(
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(14)),
            side: BorderSide(color: Color(0xFFe7e8ee), width: 1),
          ),
          margin: EdgeInsets.zero,
          color: Colors.white,
        ),
        floatingActionButtonTheme: const FloatingActionButtonThemeData(
          backgroundColor: Color(0xFF2a0441),
          foregroundColor: Colors.white,
          elevation: 4,
        ),
        textTheme: const TextTheme(
          bodyLarge: TextStyle(color: Color(0xFF1f2430), fontSize: 15),
          bodyMedium: TextStyle(color: Color(0xFF1f2430), fontSize: 15),
          titleLarge: TextStyle(color: Color(0xFF1f2430), fontWeight: FontWeight.bold, fontSize: 20),
          titleMedium: TextStyle(color: Color(0xFF1f2430), fontWeight: FontWeight.w700, fontSize: 16),
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
