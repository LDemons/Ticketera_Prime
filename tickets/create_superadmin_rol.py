"""
Script para crear el rol de Superadmin en la base de datos.
Ejecutar desde el shell de Django: python manage.py shell < tickets/create_superadmin_rol.py
"""

from tickets.models import Rol

# Crear el rol de Superadmin si no existe
superadmin_rol, created = Rol.objects.get_or_create(
    nombre='Superadmin',
    defaults={
        'descripcion': 'Superadministrador del sistema con acceso completo a gestión de usuarios, tickets, reportes y configuración.'
    }
)

if created:
    print(f"✅ Rol 'Superadmin' creado exitosamente con ID: {superadmin_rol.rol_id}")
else:
    print(f"ℹ️  El rol 'Superadmin' ya existe con ID: {superadmin_rol.rol_id}")

print(f"Descripción: {superadmin_rol.descripcion}")
