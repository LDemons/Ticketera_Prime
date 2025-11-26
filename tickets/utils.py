"""
Utilidades para el sistema de tickets
"""

def is_mobile_device(request):
    """
    Detecta si la petición viene de un dispositivo móvil
    analizando el User-Agent del navegador
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    
    mobile_keywords = [
        'android', 'iphone', 'ipad', 'ipod', 
        'blackberry', 'windows phone', 'mobile',
        'webos', 'opera mini', 'palm'
    ]
    
    return any(keyword in user_agent for keyword in mobile_keywords)
