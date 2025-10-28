from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AsignacionTicket, Comentario, Notificacion, Usuario, Rol

@receiver(post_save, sender=AsignacionTicket)
def crear_notificacion_asignacion(sender, instance, created, **kwargs):
    """
    Crea una notificación cuando se asigna un ticket a un técnico.
    """
    if created: # Solo si es una nueva asignación
        asignacion = instance
        ticket = asignacion.ticket
        destinatario = asignacion.usuario_asignado
        
        mensaje = f"Se te ha asignado el ticket #T{ticket.ticket_id:03d}: '{ticket.titulo[:30]}...'"
        
        Notificacion.objects.create(
            usuario_destino=destinatario,
            ticket=ticket,
            mensaje=mensaje
        )

@receiver(post_save, sender=Comentario)
def crear_notificacion_comentario(sender, instance, created, **kwargs):
    """
    Crea una notificación cuando hay un nuevo comentario en un ticket.
    """
    if created: # Solo si es un nuevo comentario
        comentario = instance
        ticket = comentario.ticket
        autor = comentario.autor
        destinatario = None
        mensaje = ""

        try:
            # 1. Si el autor es de TI...
            if autor.rol.nombre == 'TI':
                # ...notifica al creador del ticket (Docente)
                destinatario = ticket.usuario_creador
                mensaje = f"{autor.nombre} (TI) ha respondido a tu ticket #T{ticket.ticket_id:03d}"

            # 2. Si el autor es Docente...
            elif autor.rol.nombre == 'Docente':
                # ...notifica al técnico asignado (si hay uno)
                asignacion_activa = AsignacionTicket.objects.filter(ticket=ticket).order_by('-fecha_asignacion').first()
                if asignacion_activa:
                    destinatario = asignacion_activa.usuario_asignado
                    mensaje = f"{autor.nombre} (Docente) ha comentado en el ticket #{ticket.ticket_id}"

            # 3. Si el autor es Admin (y no es el creador)...
            elif autor.rol.nombre == 'Admin' and autor != ticket.usuario_creador:
                 # ...notifica al creador del ticket (Docente)
                destinatario = ticket.usuario_creador
                mensaje = f"El Administrador ({autor.nombre}) ha comentado tu ticket #T{ticket.ticket_id:03d}"


            # Si encontramos un destinatario (y no es él mismo), creamos la notificación
            if destinatario and destinatario != autor:
                Notificacion.objects.create(
                    usuario_destino=destinatario,
                    ticket=ticket,
                    mensaje=mensaje
                )
                
        except Rol.DoesNotExist:
            # Manejar el caso de que el Rol no exista (aunque no debería pasar)
            pass
        except Exception as e:
            # Es buena práctica imprimir errores en los signals
            print(f"Error al crear notificación: {e}")