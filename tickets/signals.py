from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import AsignacionTicket, Comentario, Notificacion, Usuario, Rol

@receiver(post_save, sender=AsignacionTicket)
def crear_notificacion_asignacion(sender, instance, created, **kwargs):
    """
    Crea una notificación cuando se asigna un ticket a un técnico.
    Incluye el comentario del admin si existe.
    """
    if created:
        asignacion = instance
        ticket = asignacion.ticket
        destinatario = asignacion.usuario_asignado
        
        # Crear mensaje base
        mensaje = f"Se te ha asignado el ticket #T{ticket.ticket_id:03d}: '{ticket.titulo[:30]}...'"
        
        # Si hay comentarios del admin en la asignación, añadirlos al mensaje
        if asignacion.comentarios and asignacion.comentarios.strip():
            mensaje += f" | Nota del Admin: {asignacion.comentarios[:50]}..."
        
        Notificacion.objects.create(
            usuario_destino=destinatario,
            ticket=ticket,
            mensaje=mensaje
        )

@receiver(post_save, sender=Comentario)
def crear_notificacion_comentario(sender, instance, created, **kwargs):
    """
    Crea una notificación cuando hay un nuevo comentario en un ticket.
    SOLO para comentarios de Docente o TI (NO Admin).
    """
    if created:
        comentario = instance
        ticket = comentario.ticket
        autor = comentario.autor
        destinatario = None
        mensaje = ""

        try:
            # 1. Si el autor es de TI...
            if autor.rol.nombre == 'TI':
                destinatario = ticket.usuario_creador
                mensaje = f"{autor.nombre} (TI) ha respondido a tu ticket #T{ticket.ticket_id:03d}"

            # 2. Si el autor es Docente...
            elif autor.rol.nombre == 'Docente':
                asignacion_activa = AsignacionTicket.objects.filter(ticket=ticket).order_by('-fecha_asignacion').first()
                if asignacion_activa:
                    destinatario = asignacion_activa.usuario_asignado
                    mensaje = f"{autor.nombre} (Docente) ha comentado en el ticket #T{ticket.ticket_id:03d}"

            # 3. REMOVIDO: El Admin ya NO crea notificaciones por comentarios
            # Los comentarios del admin solo van en la asignación inicial

            # Si encontramos un destinatario (y no es él mismo), creamos la notificación
            if destinatario and destinatario != autor:
                Notificacion.objects.create(
                    usuario_destino=destinatario,
                    ticket=ticket,
                    mensaje=mensaje
                )
                
        except Rol.DoesNotExist:
            pass
        except Exception as e:
            print(f"Error al crear notificación: {e}")


@receiver(post_save, sender=Usuario)
def crear_usuario_django(sender, instance, created, **kwargs):
    """
    Crea automáticamente un usuario Django cuando se crea un Usuario en la app.
    Si el Usuario tiene una contraseña específica, la usa; si no, pone una por defecto.
    """
    if created:
        try:
            # Verificar si ya existe un usuario Django con ese email
            if User.objects.filter(email=instance.email).exists():
                print(f"Usuario Django ya existe para {instance.email}")
                return
            
            # Generar username único a partir del email
            username_base = instance.email.split('@')[0]
            username = username_base
            
            # Si el username ya existe, agregar un número
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{username_base}{counter}"
                counter += 1
            
            # Determinar qué contraseña usar
            # Si el Usuario de la app tiene una contraseña hasheada, verificamos si es válida
            # Si no tiene o es inválida, usamos la contraseña por defecto
            if instance.contrasenia_hash and instance.contrasenia_hash.strip():
                # El Usuario ya tiene una contraseña hasheada (puesta por el admin)
                # Creamos el Django User y le asignamos el mismo hash
                django_user = User.objects.create(
                    username=username,
                    email=instance.email,
                    password=instance.contrasenia_hash,  # Usar el hash del Usuario
                    first_name=instance.nombre.split()[0] if instance.nombre else '',
                    is_active=instance.activo
                )
                print(f"✓ Usuario Django creado con contraseña personalizada: {username} ({instance.email})")
            else:
                # No tiene contraseña, usar la por defecto
                django_user = User.objects.create_user(
                    username=username,
                    email=instance.email,
                    password='ticketera2025',  # Contraseña por defecto actualizada
                    first_name=instance.nombre.split()[0] if instance.nombre else '',
                    is_active=instance.activo
                )
                print(f"✓ Usuario Django creado con contraseña por defecto: {username} ({instance.email})")
            
        except Exception as e:
            print(f"✗ Error al crear usuario Django para {instance.email}: {e}")