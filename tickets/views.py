# tickets/views.py
from django.shortcuts import render, redirect
from .models import Ticket, Usuario, AsignacionTicket, Comentario
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required 
from .forms import TicketForm, AsignacionTicketForm, GestionTicketForm, ComentarioForm
from django.utils import timezone

@login_required
def index_view(request):
    """
    Redirige al usuario a su página principal según su rol.
    """
    try:
        # Buscamos el usuario de nuestro modelo basado en el usuario de Django
        usuario = Usuario.objects.get(email=request.user.email)
        
        # Redirigimos según el nombre del rol
        if usuario.rol.nombre == 'Admin':
            return redirect('dashboard')
        elif usuario.rol.nombre == 'TI':
            return redirect('mis_asignaciones')
        elif usuario.rol.nombre == 'Docente':
            return redirect('mis_tickets')
        else:
            # Si tiene un rol desconocido, lo mandamos al login
            return redirect('login')
            
    except Usuario.DoesNotExist:
        # Si el usuario de Django no existe en nuestro modelo
        # (ej. es un superuser de Django pero no un 'Usuario' de la app)
        if request.user.is_superuser:
            return redirect('/admin/')
        else:
            return redirect('login')


@login_required
def dashboard_view(request):
    # --- BLOQUE DE PERMISO ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'Admin':
            return redirect('index') # Si no es Admin, a la salida
    except Usuario.DoesNotExist:
        return redirect('index') # Si no existe, a la salida
    # --- FIN DEL BLOQUE ---
    
    # Hacemos las consultas a la base de datos
    tickets_abiertos = Ticket.objects.filter(estado='ABIERTO').count()
    tickets_en_progreso = Ticket.objects.filter(estado='EN_PROGRESO').count()
    # Añade más contadores si lo necesitas (ej: resueltos, cerrados, etc.)

    # Pasamos los datos a la plantilla a través del contexto
    context = {
        'view_class': 'view-dashboard',
        'tickets_abiertos': tickets_abiertos,
        'tickets_en_progreso': tickets_en_progreso,
        # Puedes añadir más datos aquí, como los tickets con SLA vencido
        'sla_vencidos': 0, # <-- Por ahora lo dejamos en 0
        'tiempo_respuesta': 'N/A', # <-- Por ahora lo dejamos estático
    }
    return render(request, 'dashboard.html', context)

@login_required
def ticket_list_view(request, ticket_id=None):
    # --- BLOQUE DE PERMISO ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'Admin':
            return redirect('index') # Si no es Admin, a la salida
    except Usuario.DoesNotExist:
        return redirect('index') # Si no existe, a la salida
    # --- FIN DEL BLOQUE ---
    
    # Lógica de asignación (POST)
    if request.method == 'POST' and ticket_id:
        ticket_para_asignar = get_object_or_404(Ticket, pk=ticket_id)
        form = AsignacionTicketForm(request.POST)
        
        if form.is_valid():
            # Creamos la asignación pero no la guardamos aún
            asignacion = form.save(commit=False)
            asignacion.ticket = ticket_para_asignar
            asignacion.save()
            
            # Actualizamos el estado del ticket a "En Progreso"
            ticket_para_asignar.estado = 'EN_PROGRESO'
            ticket_para_asignar.save()
            
            # Redirigimos a la misma vista para ver el cambio
            return redirect('ticket_list')
    
    # Lógica para mostrar la lista (GET)
    tickets = Ticket.objects.select_related('usuario_creador', 'prioridad').all()
    
    ticket_seleccionado = None
    asignacion_form = None # 👈 Inicializamos el formulario

    if ticket_id:
        # Busca el ticket para mostrarlo en el panel lateral
        ticket_seleccionado = get_object_or_404(Ticket, pk=ticket_id)
        # Creamos una instancia del formulario para pasarla al template
        asignacion_form = AsignacionTicketForm() 

    print(f"ID de ticket recibido: {ticket_id}, Ticket seleccionado: {ticket_seleccionado}")

    context = {
        'view_class': 'view-tickets',
        'tickets': tickets,
        'ticket_seleccionado': ticket_seleccionado,
        'asignacion_form': asignacion_form  # Pasamos el formulario al contexto
    }
    return render(request, 'tickets_list.html', context)


@login_required
def ticket_detail_view(request, ticket_id):
    # Busca el ticket por su ID. Si no lo encuentra, muestra un error 404.
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    context = {
        'view_class': 'view-tickets', # Mantenemos el estilo de la vista de tickets
        'ticket': ticket
    }
    return render(request, 'ticket_detail.html', context)


@login_required
def mis_tickets_view(request, ticket_id=None):
    # --- BLOQUE DE PERMISO ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'Docente':
            return redirect('index') # Si no es Docente, a la salida
    except Usuario.DoesNotExist:
        return redirect('index') # Si no existe, a la salida
    # --- FIN DEL BLOQUE ---
    
    # Usamos el 'usuario' del bloque de permisos
    creador = usuario 

    ticket_seleccionado = None
    comentarios = Comentario.objects.none()
    form_comentario = None

    # --- LÓGICA POST ---
    if request.method == 'POST':
        
        # A) Lógica para AÑADIR UN COMENTARIO (si hay ticket_id en la URL)
        if ticket_id:
            ticket_para_comentar = get_object_or_404(Ticket, pk=ticket_id, usuario_creador=creador)
            form_comentario_post = ComentarioForm(request.POST)
            
            if form_comentario_post.is_valid():
                nuevo_comentario = form_comentario_post.save(commit=False)
                nuevo_comentario.ticket = ticket_para_comentar
                nuevo_comentario.autor = creador
                nuevo_comentario.save()
                return redirect('mis_tickets_detalle', ticket_id=ticket_id)
            else:
                # Si el form de comentario falla, preparamos el contexto para mostrar el error
                ticket_seleccionado = ticket_para_comentar
                comentarios = Comentario.objects.filter(ticket=ticket_seleccionado).order_by('fecha_creacion')
                form_comentario = form_comentario_post # Pasa el form con errores
        
        # B) Lógica para CREAR UN TICKET (si NO hay ticket_id en la URL)
        else:
            form_creacion = TicketForm(request.POST)
            if form_creacion.is_valid():
                ticket_nuevo = form_creacion.save(commit=False)
                ticket_nuevo.usuario_creador = creador
                ticket_nuevo.save()
                return redirect('mis_tickets')
            # Si la creación falla, el form con errores se pasará al contexto
    
    # --- LÓGICA GET (y preparación de formularios) ---
    form_creacion = TicketForm() # Formulario de la izquierda

    # Si se está viendo un ticket específico (GET request o POST fallido de comentario)
    if ticket_id:
        if not ticket_seleccionado: # Si no lo seteamos arriba por un POST fallido
            ticket_seleccionado = get_object_or_404(Ticket, pk=ticket_id, usuario_creador=creador)
            comentarios = Comentario.objects.filter(ticket=ticket_seleccionado).order_by('fecha_creacion')
            form_comentario = ComentarioForm() # Formulario de la derecha

    # Obtenemos la lista de tickets (para la izquierda)
    tickets_del_usuario = Ticket.objects.filter(usuario_creador=creador).order_by('-fecha_creacion')

    context = {
        'view_class': 'view-tickets', # Usamos la clase que permite 2 columnas
        'tickets': tickets_del_usuario,
        'form_creacion': form_creacion, # Renombrado para claridad
        'ticket_seleccionado': ticket_seleccionado,
        'comentarios': comentarios,
        'form_comentario': form_comentario # Renombrado para claridad
    }
    return render(request, 'mis_tickets.html', context)




@login_required
def mis_asignaciones_view(request):
    # --- BLOQUE DE PERMISO ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'TI':
            return redirect('index') # Si no es TI, a la salida
    except Usuario.DoesNotExist:
        return redirect('index') # Si no existe, a la salida
    # --- FIN DEL BLOQUE ---

    # Usamos el 'usuario' del bloque de permisos
    tecnico_actual = usuario 

    # Buscamos los tickets asignados a este técnico
    tickets_asignados = Ticket.objects.filter(
        asignacionticket__usuario_asignado=tecnico_actual
    ).distinct().order_by('-fecha_creacion')

    context = {
        'view_class': 'view-tickets', # Reutilizamos el estilo de la vista de tickets
        'tickets': tickets_asignados,
        'view_title': 'Mis Asignaciones' # Un título para la página
    }
    return render(request, 'mis_asignaciones.html', context)

@login_required
def gestionar_ticket_view(request, ticket_id):
    # --- BLOQUE DE PERMISO ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'TI':
            return redirect('index') # Si no es TI, a la salida
    except Usuario.DoesNotExist:
        return redirect('index') # Si no existe, a la salida
    # --- FIN DEL BLOQUE ---

    # Usamos el 'usuario' del bloque de permisos
    tecnico_actual = usuario
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    
    # (El resto de la lógica de la vista)
    if request.method == 'POST':
        form = GestionTicketForm(request.POST)
        if form.is_valid():
            # 1. Actualizar el estado del Ticket
            nuevo_estado = form.cleaned_data['estado']
            ticket.estado = nuevo_estado
            
            if nuevo_estado in ['CERRADO', 'RESUELTO']:
                ticket.cerrado_en = timezone.now()
            
            ticket.save()

            # 2. Crear el nuevo comentario
            contenido_comentario = form.cleaned_data['contenido']
            if contenido_comentario: 
                nuevo_comentario = form.save(commit=False)
                nuevo_comentario.ticket = ticket
                nuevo_comentario.autor = tecnico_actual
                nuevo_comentario.save()

            return redirect('mis_asignaciones')
    else:
        form = GestionTicketForm(initial={'estado': ticket.estado})

    comentarios = Comentario.objects.filter(ticket=ticket).order_by('fecha_creacion')

    context = {
        'view_class': 'view-tickets',
        'ticket': ticket,
        'form': form,
        'comentarios': comentarios
    }
    return render(request, 'gestionar_ticket.html', context)