#!/usr/bin/env python
"""
Script para verificar la sincronización de usuarios entre Django y la App
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticketera_project.settings')
django.setup()

from tickets.models import Usuario
from django.contrib.auth.models import User

print("\n" + "="*70)
print("VERIFICACIÓN DE SINCRONIZACIÓN DE USUARIOS")
print("="*70 + "\n")

print(f"Total usuarios en tickets_usuario: {Usuario.objects.count()}")
print(f"Total usuarios en auth_user: {User.objects.count()}\n")

print("Verificando sincronización:\n")

problemas = []

for usuario_app in Usuario.objects.all():
    try:
        django_user = User.objects.get(email__iexact=usuario_app.email)
        # Verificar que estén sincronizados
        if django_user.is_active != usuario_app.activo:
            problemas.append(f"  [WARN] {usuario_app.email}: Estado desincronizado (Django: {django_user.is_active}, App: {usuario_app.activo})")
        else:
            print(f"  [OK] {usuario_app.email} - {usuario_app.nombre} ({usuario_app.rol.nombre if usuario_app.rol else 'Sin rol'})")
    except User.DoesNotExist:
        problemas.append(f"  [ERROR] {usuario_app.email}: Existe en App pero NO en Django (no podrá hacer login)")

if problemas:
    print("\n" + "="*70)
    print("PROBLEMAS ENCONTRADOS:")
    print("="*70)
    for problema in problemas:
        print(problema)
else:
    print("\n[OK] Todos los usuarios están correctamente sincronizados!")

print("\n" + "="*70 + "\n")
