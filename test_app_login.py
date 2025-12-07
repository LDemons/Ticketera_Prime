"""
Prueba final del login - Simula exactamente lo que hace la app móvil
"""
import requests
import json

API_URL = "http://localhost:8000/api/v1/auth/login/"

print("=" * 70)
print("PRUEBA DE LOGIN - APP MÓVIL")
print("=" * 70)

# Usuarios de prueba con diferentes formatos de email
test_cases = [
    {"email": "Paulo777G@gmail.com", "desc": "Email con mayúsculas (Paulo)"},
    {"email": "paulo777g@gmail.com", "desc": "Email en minúsculas (Paulo)"},
    {"email": "masterticket@gmail.com", "desc": "Email normal (Admin)"},
    {"email": "duoc.ti@gmail.com", "desc": "Email recién creado (TI)"},
]

print("\nElige un usuario para probar:")
for i, test in enumerate(test_cases, 1):
    print(f"{i}. {test['desc']}: {test['email']}")
print("5. Otro email")

choice = input("\nOpción (1-5): ").strip()

if choice == "5":
    email = input("Ingresa el email: ").strip()
else:
    try:
        email = test_cases[int(choice) - 1]["email"]
    except:
        print("Opción inválida")
        exit()

password = input("Ingresa la contraseña: ").strip()

print(f"\n→ Enviando request a: {API_URL}")
print(f"→ Email: {email}")
print(f"→ Password: {'*' * len(password)}")
print("-" * 70)

try:
    response = requests.post(
        API_URL,
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    
    print(f"\n✓ Status Code: {response.status_code}")
    
    try:
        response_data = response.json()
        print(f"\n✓ Response:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print(f"\n{'='*70}")
            print("✓✓✓ LOGIN EXITOSO ✓✓✓")
            print(f"{'='*70}")
            print(f"\nToken: {response_data.get('token', 'N/A')}")
            user = response_data.get('user', {})
            print(f"Usuario: {user.get('nombre', 'N/A')}")
            print(f"Email: {user.get('email', 'N/A')}")
            print(f"Rol: {user.get('rol', 'N/A')}")
        else:
            print(f"\n{'='*70}")
            print("✗✗✗ LOGIN FALLIDO ✗✗✗")
            print(f"{'='*70}")
            print(f"\nError: {response_data.get('error', 'Desconocido')}")
            
    except ValueError:
        print(f"\n✗ Response no es JSON válido:")
        print(response.text[:500])
        
except requests.exceptions.ConnectionError:
    print("\n✗ ERROR: No se pudo conectar al servidor")
    print("  → Asegúrate de que el servidor esté corriendo:")
    print("     python manage.py runserver")
except requests.exceptions.Timeout:
    print("\n✗ ERROR: Timeout - El servidor no respondió a tiempo")
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
