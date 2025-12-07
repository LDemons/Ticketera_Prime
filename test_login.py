"""
Script de prueba para verificar el login con email
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticketera_project.settings')
django.setup()

from django.contrib.auth.models import User
from tickets.models import Usuario

print("=" * 50)
print("USUARIOS DE DJANGO (User):")
print("=" * 50)
for user in User.objects.all()[:10]:
    print(f"Username: {user.username:20} | Email: {user.email:30} | Activo: {user.is_active}")

print("\n" + "=" * 50)
print("USUARIOS DE LA APP (Usuario):")
print("=" * 50)
for usuario in Usuario.objects.select_related('rol').all()[:10]:
    print(f"Nombre: {usuario.nombre:20} | Email: {usuario.email:30} | Activo: {usuario.activo}")

print("\n" + "=" * 50)
print("VERIFICANDO CORRESPONDENCIA:")
print("=" * 50)

# Verificar si los emails coinciden
usuarios_app = Usuario.objects.all()
for usuario_app in usuarios_app[:10]:
    try:
        django_user = User.objects.get(email=usuario_app.email)
        print(f"✓ {usuario_app.email} - Django User: {django_user.username}")
    except User.DoesNotExist:
        print(f"✗ {usuario_app.email} - NO TIENE USUARIO DJANGO")
    except User.MultipleObjectsReturned:
        print(f"⚠ {usuario_app.email} - MÚLTIPLES USUARIOS DJANGO")

print("\n" + "=" * 50)
print("PRUEBA DE AUTENTICACIÓN:")
print("=" * 50)

# Intentar autenticar con un usuario de ejemplo
test_email = input("Ingresa el email para probar (o Enter para saltar): ").strip()
if test_email:
    try:
        django_user = User.objects.get(email=test_email)
        print(f"✓ Usuario Django encontrado: {django_user.username}")
        
        test_password = input("Ingresa la contraseña para probar: ").strip()
        if django_user.check_password(test_password):
            print("✓ Contraseña correcta")
            
            usuario_app = Usuario.objects.get(email=test_email)
            print(f"✓ Usuario App encontrado: {usuario_app.nombre}")
            print(f"✓ Rol: {usuario_app.rol.nombre}")
            print(f"✓ Activo: {usuario_app.activo}")
        else:
            print("✗ Contraseña incorrecta")
    except User.DoesNotExist:
        print(f"✗ No existe usuario Django con email: {test_email}")
    except Usuario.DoesNotExist:
        print(f"✗ No existe usuario App con email: {test_email}")
    except Exception as e:
        print(f"✗ Error: {e}")
