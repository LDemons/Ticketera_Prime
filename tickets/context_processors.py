from .models import Notificacion, Usuario

def notificaciones_context(request):
    """
    Añade el conteo de notificaciones no leídas al contexto de todas las plantillas.
    """
    if request.user.is_authenticated:
        try:
            # Buscamos nuestro modelo de Usuario basado en el usuario de Django
            usuario_app = Usuario.objects.get(email=request.user.email)
            
            # Contamos las notificaciones no leídas para ESE usuario
            conteo = Notificacion.objects.filter(
                usuario_destino=usuario_app, 
                leido=False
            ).count()
            
            return {
                'notificaciones_conteo_no_leidas': conteo
            }
        except Usuario.DoesNotExist:
            # Si el usuario es, por ej., un Superuser de Django pero no 
            # un Usuario de nuestra app, no tendrá notificaciones.
            return {
                'notificaciones_conteo_no_leidas': 0
            }
    
    # Si no está autenticado, no hay notificaciones
    return {
        'notificaciones_conteo_no_leidas': 0
    }