"""
Script para probar el login de la API
"""
import requests
import json

API_URL = "http://localhost:8000/api/v1/auth/login/"

print("=" * 60)
print("PRUEBA DE LOGIN CON EMAIL")
print("=" * 60)

# Probar con Paulo
test_users = [
    {"email": "Paulo777G@gmail.com", "password": "paulo123"},  # Ajusta la contraseña real
    {"email": "masterticket@gmail.com", "password": "master123"},
    {"email": "duoc.docente@gmail.com", "password": "ticketera2024"},  # Usuario recién creado
]

print("\nIngresa el email del usuario a probar:")
email = input("> ").strip()

if not email:
    print("No se ingresó email. Prueba cancelada.")
else:
    password = input("Ingresa la contraseña: ").strip()
    
    print(f"\nProbando login con: {email}")
    print("-" * 60)
    
    try:
        response = requests.post(
            API_URL,
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✓ LOGIN EXITOSO")
        else:
            print("\n✗ LOGIN FALLIDO")
            
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: No se pudo conectar al servidor")
        print("  Asegúrate de que el servidor esté corriendo: python manage.py runserver")
    except Exception as e:
        print(f"✗ ERROR: {e}")
