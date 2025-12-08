#!/usr/bin/env python
"""
Script de prueba: Crear nuevo usuario y verificar que puede hacer login
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticketera_project.settings')
django.setup()

from tickets.models import Usuario, Rol
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

# Limpiar usuario de prueba si existe
test_email = "test.docente@gmail.com"
test_username = test_email.split('@')[0]
print(f"\n[INFO] Limpiando usuario de prueba si existe: {test_email}")
Usuario.objects.filter(email=test_email).delete()
User.objects.filter(email=test_email).delete()
User.objects.filter(username=test_username).delete()

# Crear nuevo usuario SIN contraseña (para probar el default)
print(f"[INFO] Creando nuevo usuario de prueba...")
rol_docente = Rol.objects.get(nombre="Docente")

nuevo_usuario = Usuario.objects.create(
    nombre="Test Docente",
    email=test_email,
    rut=99887766,  # RUT de prueba (solo números)
    rol=rol_docente,
    activo=True,
    contrasenia_hash=make_password('ticketera2025')  # El signal usará esta contraseña
)

print(f"[OK] Usuario creado: {nuevo_usuario.nombre} ({nuevo_usuario.email})")
print(f"[OK] El signal crear_usuario_django debería haber creado el Django User automáticamente")

# Verificar que el Django User fue creado por el signal
from django.contrib.auth import authenticate

try:
    django_user = User.objects.get(email=test_email)
    print(f"[OK] Django User encontrado: {django_user.username}")
    
    # Verificar que puede autenticarse
    auth_user = authenticate(username=django_user.username, password='ticketera2025')
    if auth_user:
        print(f"[OK] Autenticación exitosa con contraseña por defecto 'ticketera2025'")
        print(f"\n{'='*70}")
        print("RESUMEN:")
        print(f"{'='*70}")
        print(f"Email: {test_email}")
        print(f"Username: {django_user.username}")
        print(f"Password: ticketera2025")
        print(f"Puede hacer login en la app: SÍ")
        print(f"{'='*70}\n")
        print("[INFO] Usuario de prueba listo para probar en la app móvil")
    else:
        print("[ERROR] No se pudo autenticar")
except User.DoesNotExist:
    print("[ERROR] El Django User NO fue creado por el signal")
