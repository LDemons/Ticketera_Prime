"""
Script para crear datos iniciales: roles, categorías, prioridades y usuario de prueba
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticketera_project.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import Rol, Categoria, Prioridad, Usuario

print("Configurando datos iniciales...\n")

# Crear roles (con IDs específicos)
roles_data = [
    {'rol_id': 1, 'nombre': 'Superadmin', 'descripcion': 'Superadministrador del sistema con acceso completo'},
    {'rol_id': 2, 'nombre': 'Admin', 'descripcion': 'Administrador con acceso a gestión de tickets y usuarios'},
    {'rol_id': 3, 'nombre': 'TI', 'descripcion': 'Técnico de TI que resuelve tickets'},
    {'rol_id': 4, 'nombre': 'Docente', 'descripcion': 'Docente que puede crear y consultar tickets'},
]

print("Creando roles...")
for rol_data in roles_data:
    rol, created = Rol.objects.get_or_create(
        rol_id=rol_data['rol_id'],
        defaults={'nombre': rol_data['nombre'], 'descripcion': rol_data['descripcion']}
    )
    status = "[CREADO]" if created else "[YA EXISTE]"
    print(f"  {status}: {rol.nombre}")

# Crear categorías
categorias_data = [
    'Hardware',
    'Software',
    'Red',
    'Infraestructura',
    'Soporte',
    'Otro'
]

print("\nCreando categorias...")
for nombre in categorias_data:
    cat, created = Categoria.objects.get_or_create(nombre=nombre)
    status = "[CREADA]" if created else "[YA EXISTE]"
    print(f"  {status}: {nombre}")

# Crear prioridades
prioridades_data = [
    {'Tipo_Nivel': 'BAJO', 'sla_horas': 168},  # 7 días
    {'Tipo_Nivel': 'MEDIO', 'sla_horas': 72},  # 3 días
    {'Tipo_Nivel': 'ALTO', 'sla_horas': 24},   # 1 día
]

print("\nCreando prioridades...")
for prior_data in prioridades_data:
    prior, created = Prioridad.objects.get_or_create(
        Tipo_Nivel=prior_data['Tipo_Nivel'],
        defaults={'sla_horas': prior_data['sla_horas']}
    )
    status = "[CREADA]" if created else "[YA EXISTE]"
    print(f"  {status}: {prior.Tipo_Nivel} (SLA: {prior.sla_horas}h)")

# Crear usuario de prueba
print("\nCreando usuario de prueba...")
try:
    from django.contrib.auth.hashers import make_password
    
    rol_docente = Rol.objects.get(nombre='Docente')
    
    usuario, created = Usuario.objects.get_or_create(
        rut=12345678,
        defaults={
            'dv': '9',
            'nombre': 'Juan Pérez',
            'email': 'docente@test.com',
            'contrasenia_hash': make_password('test123'),
            'rol': rol_docente,
            'activo': True,
        }
    )
    
    status = "[CREADO]" if created else "[YA EXISTE]"
    print(f"  {status}: {usuario.email}")
    
    print("\n" + "="*50)
    print("DATOS DE PRUEBA LISTOS")
    print("="*50)
    print(f"\nUsuario de prueba creado")
    print(f"Rol: Docente")
    print("\nVerifica las credenciales en tu gestor de contrasenas\n")
    
except Exception as e:
    print(f"  [ERROR]: {e}")
