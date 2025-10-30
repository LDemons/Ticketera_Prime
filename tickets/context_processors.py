from .models import Notificacion, Usuario

def notificaciones_context(request):
    """
    Añade el conteo de notificaciones Y el rol del usuario 
    al contexto de todas las plantillas.
    """
    contexto = {
        'notificaciones_conteo_no_leidas': 0,
        'usuario_rol': None # Valor por defecto
    }

    if request.user.is_authenticated:
        try:
            # Buscamos nuestro modelo de Usuario
            usuario_app = Usuario.objects.get(email=request.user.email)
            
            # Contamos las notificaciones
            conteo = Notificacion.objects.filter(
                usuario_destino=usuario_app, 
                leido=False
            ).count()
            
            # Añadimos los datos al contexto
            contexto['notificaciones_conteo_no_leidas'] = conteo
            contexto['usuario_rol'] = usuario_app.rol.nombre # <-- ¡AÑADIDO!
            
        except Usuario.DoesNotExist:
            # Si es un Superuser de Django pero no un Usuario de la app
            if request.user.is_superuser:
                 contexto['usuario_rol'] = 'Superuser' # Un rol especial
            
    return contexto