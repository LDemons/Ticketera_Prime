#!/usr/bin/env python
"""
Script para crear usuario de prueba para la app móvil
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticketera_project.settings')
django.setup()

from tickets.models import Usuario, Rol
from django.contrib.auth.hashers import make_password

# NOTA: Cambiar estos valores antes de usar en producción
TEST_EMAIL = 'docente@test.com'
TEST_PASSWORD = 'test123'  # Solo para desarrollo local

# Crear o actualizar rol Docente
rol_docente, created = Rol.objects.get_or_create(
    rol_id=4,
    defaults={'nombre': 'Docente'}
)
if created:
    print("[OK] Rol 'Docente' creado")
else:
    print("[INFO] Rol 'Docente' ya existe")

# Crear o actualizar usuario de prueba
try:
    usuario = Usuario.objects.get(email=TEST_EMAIL)
    # Si existe, actualizar contraseña
    usuario.contraseña = make_password(TEST_PASSWORD)
    usuario.save()
    print(f"[OK] Usuario '{TEST_EMAIL}' actualizado")
except Usuario.DoesNotExist:
    # Si no existe, crearlo
    usuario = Usuario.objects.create(
        rut=12345678,
        nombre='Docente Test',
        email=TEST_EMAIL,
        contraseña=make_password(TEST_PASSWORD),
        rol=rol_docente,
        activo=True
    )
    print(f"[OK] Usuario '{TEST_EMAIL}' creado")

print("\n" + "="*50)
print("USUARIO DE PRUEBA CREADO")
print("="*50)
print("Verifica las credenciales en tu gestor de contraseñas local")
print("="*50)
