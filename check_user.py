#!/usr/bin/env python
"""
Script para verificar si un usuario existe y puede hacer login
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticketera_project.settings')
django.setup()

from tickets.models import Usuario
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

email_to_check = 'duoc.docente@gmail.com'

print(f"\n{'='*60}")
print(f"VERIFICANDO USUARIO: {email_to_check}")
print(f"{'='*60}\n")

# Verificar en User de Django
print("1. Usuario en Django (auth_user):")
try:
    django_user = User.objects.get(email__iexact=email_to_check)
    print(f"   [OK] Encontrado")
    print(f"   - Username: {django_user.username}")
    print(f"   - Email: {django_user.email}")
    print(f"   - Is Active: {django_user.is_active}")
    print(f"   - Has Password: {bool(django_user.password)}")
    
    # Verificar contraseña
    password_to_test = 'duoc12345'
    password_ok = django_user.check_password(password_to_test)
    print(f"   - Password '{password_to_test}' correcta: {password_ok}")
except User.DoesNotExist:
    print(f"   [ERROR] NO encontrado en auth_user")
    django_user = None

print()

# Verificar en Usuario de la app
print("2. Usuario en App (tickets_usuario):")
try:
    usuario_app = Usuario.objects.get(email__iexact=email_to_check)
    print(f"   [OK] Encontrado")
    print(f"   - RUT: {usuario_app.rut}")
    print(f"   - Nombre: {usuario_app.nombre}")
    print(f"   - Email: {usuario_app.email}")
    print(f"   - Rol: {usuario_app.rol.nombre if usuario_app.rol else 'Sin rol'}")
    print(f"   - Activo: {usuario_app.activo}")
except Usuario.DoesNotExist:
    print(f"   [ERROR] NO encontrado en tickets_usuario")
    usuario_app = None

print()

# Diagnóstico
print("3. DIAGNÓSTICO:")
if django_user and usuario_app:
    if django_user.is_active and usuario_app.activo:
        if django_user.check_password('duoc12345'):
            print("   [OK] Usuario configurado correctamente, debería poder hacer login")
        else:
            print("   [ERROR] Contraseña incorrecta en Django User")
    else:
        print(f"   [ERROR] Usuario inactivo (Django: {django_user.is_active}, App: {usuario_app.activo})")
elif django_user and not usuario_app:
    print("   [ERROR] Usuario existe en Django pero NO en la app")
elif usuario_app and not django_user:
    print("   [ERROR] Usuario existe en la app pero NO en Django (no puede hacer login)")
else:
    print("   [ERROR] Usuario NO existe en ninguna tabla")

print()

# Listar todos los usuarios disponibles
print("4. TODOS LOS USUARIOS DISPONIBLES:")
print("\n   Usuarios Django:")
for u in User.objects.all()[:10]:
    print(f"   - {u.email or u.username}")
    
print("\n   Usuarios App:")
for u in Usuario.objects.all()[:10]:
    print(f"   - {u.email} ({u.nombre}) - {u.rol.nombre if u.rol else 'Sin rol'}")

print(f"\n{'='*60}\n")
