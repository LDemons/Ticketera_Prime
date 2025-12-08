"""
Script de prueba completa del login para diagnosticar problemas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticketera_project.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import Usuario
from rest_framework.authtoken.models import Token

print("=" * 70)
print("DIAGNÓSTICO COMPLETO DEL SISTEMA DE LOGIN")
print("=" * 70)

# Test 1: Verificar usuarios
print("\n1. USUARIOS EN EL SISTEMA:")
print("-" * 70)
usuarios_app = Usuario.objects.all()
for usuario_app in usuarios_app:
    print(f"\n  Usuario App: {usuario_app.nombre}")
    print(f"  Email: {usuario_app.email}")
    print(f"  Activo: {usuario_app.activo}")
    print(f"  Rol: {usuario_app.rol.nombre}")
    
    # Buscar usuario Django correspondiente
    try:
        django_user = User.objects.get(email=usuario_app.email)
        print(f"  ✓ Django User: {django_user.username} (activo: {django_user.is_active})")
        
        # Verificar token
        token = Token.objects.filter(user=django_user).first()
        if token:
            print(f"  ✓ Token: {token.key[:20]}...")
        else:
            print(f"  ⚠ Sin token (se creará al hacer login)")
            
    except User.DoesNotExist:
        print(f"  ✗ NO TIENE USUARIO DJANGO - NO PUEDE HACER LOGIN")
    except User.MultipleObjectsReturned:
        print(f"  ⚠ MÚLTIPLES USUARIOS DJANGO CON ESTE EMAIL")

# Test 2: Simular login
print("\n\n2. SIMULACIÓN DE LOGIN:")
print("-" * 70)

email = input("\nIngresa el email para probar el login: ").strip()
if email:
    password = input("Ingresa la contraseña: ").strip()
    
    print(f"\n→ Intentando login con: {email}")
    
    # Paso 1: Buscar usuario Django
    try:
        django_user = User.objects.get(email=email)
        print(f"  ✓ Usuario Django encontrado: {django_user.username}")
    except User.DoesNotExist:
        print(f"  ✗ ERROR: No existe usuario Django con email: {email}")
        print(f"  → SOLUCIÓN: Ejecutar 'python sync_django_users.py'")
        exit()
    
    # Paso 2: Verificar contraseña
    if django_user.check_password(password):
        print(f"  ✓ Contraseña correcta")
    else:
        print(f"  ✗ ERROR: Contraseña incorrecta")
        print(f"  → Verifica la contraseña o usa 'ticketera2024' si es nueva")
        exit()
    
    # Paso 3: Buscar usuario en la app
    try:
        usuario_app = Usuario.objects.select_related('rol').get(email=email)
        print(f"  ✓ Usuario App encontrado: {usuario_app.nombre}")
        print(f"    - Rol: {usuario_app.rol.nombre}")
        print(f"    - Activo: {usuario_app.activo}")
    except Usuario.DoesNotExist:
        print(f"  ✗ ERROR: Usuario no encontrado en la tabla Usuario")
        exit()
    
    # Paso 4: Verificar que esté activo
    if not usuario_app.activo:
        print(f"  ✗ ERROR: Usuario inactivo")
        exit()
    
    # Paso 5: Obtener o crear token
    token, created = Token.objects.get_or_create(user=django_user)
    if created:
        print(f"  ✓ Token creado: {token.key}")
    else:
        print(f"  ✓ Token existente: {token.key}")
    
    # Respuesta simulada
    print(f"\n  ✓✓✓ LOGIN EXITOSO ✓✓✓")
    print(f"\n  Respuesta de la API:")
    print(f"  {{")
    print(f'    "token": "{token.key}",')
    print(f'    "user": {{')
    print(f'      "rut": {usuario_app.rut},')
    print(f'      "nombre": "{usuario_app.nombre}",')
    print(f'      "email": "{usuario_app.email}",')
    print(f'      "rol": "{usuario_app.rol.nombre}"')
    print(f'    }}')
    print(f'  }}')

print("\n" + "=" * 70)
