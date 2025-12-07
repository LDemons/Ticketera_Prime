"""
Script de prueba para el endpoint de cambio de contraseña
"""
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

print("=" * 70)
print("PRUEBA: CAMBIAR CONTRASEÑA")
print("=" * 70)

# Paso 1: Login
print("\n1. Login para obtener token:")
email = input("Email: ").strip()
password = input("Contraseña actual: ").strip()

login_response = requests.post(
    f"{API_BASE}/auth/login/",
    json={"email": email, "password": password}
)

if login_response.status_code != 200:
    print(f"✗ Login fallido: {login_response.json()}")
    exit()

token = login_response.json()["token"]
user = login_response.json()["user"]
print(f"✓ Login exitoso como: {user['nombre']} ({user['rol']})")
print(f"✓ Token: {token[:20]}...")

# Paso 2: Cambiar contraseña
print("\n2. Cambiar contraseña:")
current_password = password  # Ya la tenemos del login
new_password = input("Nueva contraseña (mínimo 6 caracteres): ").strip()
confirm_password = input("Confirmar nueva contraseña: ").strip()

change_response = requests.post(
    f"{API_BASE}/auth/change-password/",
    json={
        "current_password": current_password,
        "new_password": new_password,
        "confirm_password": confirm_password
    },
    headers={"Authorization": f"Token {token}"}
)

print(f"\nStatus Code: {change_response.status_code}")
print(f"Response:")
print(json.dumps(change_response.json(), indent=2, ensure_ascii=False))

if change_response.status_code == 200:
    new_token = change_response.json()["token"]
    print(f"\n{'='*70}")
    print("✓✓✓ CONTRASEÑA CAMBIADA EXITOSAMENTE ✓✓✓")
    print(f"{'='*70}")
    print(f"\nNuevo Token: {new_token}")
    print("\n⚠ IMPORTANTE: Guarda este nuevo token")
    print("  El token anterior ya no funciona")
    
    # Paso 3: Verificar que el nuevo token funciona
    print("\n3. Verificando nuevo token...")
    profile_response = requests.get(
        f"{API_BASE}/auth/profile/",
        headers={"Authorization": f"Token {new_token}"}
    )
    
    if profile_response.status_code == 200:
        print("✓ Nuevo token funciona correctamente")
    else:
        print("✗ Problema con el nuevo token")
    
    # Paso 4: Verificar que el viejo token no funciona
    print("\n4. Verificando que el token viejo está invalidado...")
    old_profile_response = requests.get(
        f"{API_BASE}/auth/profile/",
        headers={"Authorization": f"Token {token}"}
    )
    
    if old_profile_response.status_code == 401:
        print("✓ Token viejo correctamente invalidado")
    else:
        print("⚠ Token viejo aún funciona (esto no debería pasar)")
    
    # Paso 5: Probar login con nueva contraseña
    print("\n5. Probando login con nueva contraseña...")
    new_login_response = requests.post(
        f"{API_BASE}/auth/login/",
        json={"email": email, "password": new_password}
    )
    
    if new_login_response.status_code == 200:
        print("✓ Login exitoso con nueva contraseña")
        print(f"✓ Token del login: {new_login_response.json()['token'][:20]}...")
    else:
        print("✗ Login fallido con nueva contraseña")
        
else:
    print(f"\n{'='*70}")
    print("✗✗✗ ERROR AL CAMBIAR CONTRASEÑA ✗✗✗")
    print(f"{'='*70}")
    error = change_response.json().get('error', 'Error desconocido')
    print(f"\nError: {error}")

print("\n" + "=" * 70)
