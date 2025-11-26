from django import template
import hashlib
from django.urls import reverse

register = template.Library()

@register.filter(name='split_at_hash')
def split_at_hash(value):
    """
    Parte un string en el primer '#' y devuelve una lista.
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
        return 'hsl(210, 65%, 50%)'  # Color azul por defecto
    
    # Generar hash del nombre
    hash_object = hashlib.md5(username.encode())
    hash_hex = hash_object.hexdigest()
    
    # Usar los primeros 8 caracteres del hash para generar un número
    hash_int = int(hash_hex[:8], 16)
    
    # Generar un tono (hue) entre 0 y 360
    hue = hash_int % 360
    
    # Mantener saturación y luminosidad fijas para consistencia visual
    saturation = 65  # Saturación media-alta
    lightness = 50   # Luminosidad media
    
    return f'hsl({hue}, {saturation}%, {lightness}%)'


@register.simple_tag(takes_context=True)
def ticket_url(context, ticket_id, rol):
    """
    Genera la URL correcta para ver un ticket según el dispositivo y el rol del usuario.
    - PC: Usa vistas con panel lateral (mis_asignaciones, mis_tickets, ticket_detail)
    - Móvil: Usa vistas de detalle completo (mis_asignaciones_detalle, mis_tickets_detalle, ticket_detail)
    """
    request = context.get('request')
    
    # Detectar si es móvil
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower() if request else ''
    mobile_keywords = ['android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone', 'mobile', 'webos', 'opera mini', 'palm']
    is_mobile = any(keyword in user_agent for keyword in mobile_keywords)
    
    # Generar URL según rol y dispositivo
    if rol == 'Docente':
        if is_mobile:
            return reverse('mis_tickets_detalle', args=[ticket_id])
        else:
            return reverse('mis_tickets', args=[ticket_id])
    elif rol == 'TI':
        if is_mobile:
            return reverse('mis_asignaciones_detalle', args=[ticket_id])
        else:
            return reverse('mis_asignaciones', args=[ticket_id])
    elif rol in ['Admin', 'Superadmin']:
        return reverse('ticket_detail', args=[ticket_id])
    else:
        return '#'