"""
Script para agregar la categoría 'Pendiente de clasificación'
para tickets creados por docentes
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticketera_project.settings')
django.setup()

from tickets.models import Categoria

# Crear categoría si no existe
categoria, created = Categoria.objects.get_or_create(
    nombre='Pendiente de clasificación',
    defaults={
        'descripcion': 'Categoría temporal para tickets creados por docentes que aún no han sido clasificados por el administrador'
    }
)

if created:
    print(f"✓ Categoría creada: {categoria.nombre} (ID: {categoria.categoria_id})")
else:
    print(f"✓ La categoría ya existe: {categoria.nombre} (ID: {categoria.categoria_id})")
