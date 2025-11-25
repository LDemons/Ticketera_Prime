from django import template
import hashlib

register = template.Library()

@register.filter(name='split_at_hash')
def split_at_hash(value):
    """
    Parte un string en el primer '#' y devuelve una lista.
    Volvemos a añadir el '#' a la segunda parte.
    """
    if '#' in value:
        parts = value.split('#', 1)
        return [parts[0], '#' + parts[1]]
    else:
        return [value]

@register.filter(name='user_color')
def user_color(username):
    """
    Genera un color consistente basado en el nombre de usuario.
    Retorna un color en formato HSL con saturación y luminosidad fijas.
    """
    if not username:
        return 'hsl(210, 70%, 55%)'  # Color por defecto (azul)
    
    # Generar hash del nombre
    hash_object = hashlib.md5(username.encode())
    hash_hex = hash_object.hexdigest()
    
    # Usar los primeros 8 caracteres del hash para generar un número
    hash_int = int(hash_hex[:8], 16)
    
    # Generar un tono (hue) entre 0 y 360
    hue = hash_int % 360
    
    # Mantener saturación y luminosidad fijas para consistencia visual
    saturation = 65  # Saturación media-alta
    lightness = 50   # Luminosidad media (ni muy claro ni muy oscuro)
    
    return f'hsl({hue}, {saturation}%, {lightness}%)'