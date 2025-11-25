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

# Crear o actualizar rol Docente
rol_docente, created = Rol.objects.get_or_create(
    rol_id=4,
    defaults={'nombre': 'Docente'}
)
if created:
    print("✓ Rol 'Docente' creado")
else:
    print("✓ Rol 'Docente' ya existe")

# Crear o actualizar usuario de prueba
try:
    usuario = Usuario.objects.get(email='docente@test.com')
    # Si existe, actualizar contraseña
    usuario.contraseña = make_password('test123')
    usuario.save()
    print("✓ Usuario 'docente@test.com' actualizado con contraseña 'test123'")
except Usuario.DoesNotExist:
    # Si no existe, crearlo
    usuario = Usuario.objects.create(
        rut=12345678,
        nombre='Docente Test',
        email='docente@test.com',
        contraseña=make_password('test123'),
        rol=rol_docente,
        activo=True
    )
    print("✓ Usuario 'docente@test.com' creado con contraseña 'test123'")

print("\n" + "="*50)
print("CREDENCIALES PARA LA APP MÓVIL:")
print("="*50)
print(f"Email:    docente@test.com")
print(f"Password: test123")
print("="*50)
