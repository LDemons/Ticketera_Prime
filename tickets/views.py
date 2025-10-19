# tickets/views.py
from django.shortcuts import render, redirect
from .models import Ticket, Usuario, AsignacionTicket, Comentario
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required 
from .forms import TicketForm, AsignacionTicketForm, GestionTicketForm
from django.utils import timezone


def dashboard_view(request):
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
def mis_tickets_view(request):
    # 👇 ¡AHORA USAMOS EL USUARIO REAL!
    usuario_actual = request.user 

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket_nuevo = form.save(commit=False)
            # Buscamos nuestro modelo Usuario basado en el usuario de Django
            creador = Usuario.objects.get(email=usuario_actual.email)
            ticket_nuevo.usuario_creador = creador
            ticket_nuevo.save()
            return redirect('mis_tickets')
    else:
        form = TicketForm()

    # Obtenemos los tickets del usuario real
    tickets_del_usuario = Ticket.objects.filter(usuario_creador__email=usuario_actual.email).order_by('-fecha_creacion')

    context = {
        'view_class': 'view-tickets',
        'tickets': tickets_del_usuario,
        'form': form
    }
    return render(request, 'mis_tickets.html', context)

@login_required # 👈 Protegemos la vista
def mis_asignaciones_view(request):
    try:
        # 1. Obtenemos el usuario 'Técnico' de nuestro modelo 'Usuario'
        #    basado en el email del usuario de Django que se logueó.
        tecnico_actual = Usuario.objects.get(email=request.user.email)
    except Usuario.DoesNotExist:
        # Si el usuario de Django no existe en nuestro modelo Usuario
        # (ej. es un superuser o un docente), no mostramos ningún ticket.
        tecnico_actual = None

    if tecnico_actual:
        # 2. Buscamos los tickets que están asignados a este técnico
        #    Usamos 'asignacionticket__usuario_asignado' para 'saltar'
        #    del modelo Ticket al modelo AsignacionTicket
        tickets_asignados = Ticket.objects.filter(
            asignacionticket__usuario_asignado=tecnico_actual
        ).distinct().order_by('-fecha_creacion')
    else:
        tickets_asignados = Ticket.objects.none()

    context = {
        'view_class': 'view-tickets', # Reutilizamos el estilo de la vista de tickets
        'tickets': tickets_asignados,
        'view_title': 'Mis Asignaciones' # Un título para la página
    }
    return render(request, 'mis_asignaciones.html', context)

@login_required
def gestionar_ticket_view(request, ticket_id):
    # Obtenemos el ticket que se va a gestionar
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    
    # Obtenemos el usuario técnico (asumimos que está logueado)
    try:
        tecnico_actual = Usuario.objects.get(email=request.user.email)
    except Usuario.DoesNotExist:
        # Si no es un usuario de nuestro modelo, no puede gestionar
        return redirect('dashboard') # O mostrar un error

    if request.method == 'POST':
        form = GestionTicketForm(request.POST)
        if form.is_valid():
            # 1. Actualizar el estado del Ticket
            nuevo_estado = form.cleaned_data['estado']
            ticket.estado = nuevo_estado
            
            # Si el estado es 'CERRADO' o 'RESUELTO', guardamos la fecha
            if nuevo_estado in ['CERRADO', 'RESUELTO']:
                ticket.cerrado_en = timezone.now()
            
            ticket.save()

            # 2. Crear el nuevo comentario
            contenido_comentario = form.cleaned_data['contenido']
            if contenido_comentario: # Solo si el técnico escribió algo
                nuevo_comentario = form.save(commit=False)
                nuevo_comentario.ticket = ticket
                nuevo_comentario.autor = tecnico_actual
                nuevo_comentario.save()

            # 3. Redirigir de vuelta a la lista de asignaciones
            return redirect('mis_asignaciones')
    else:
        # Si es GET, mostramos el formulario con el estado actual del ticket
        form = GestionTicketForm(initial={'estado': ticket.estado})

    # Obtenemos todos los comentarios existentes para este ticket
    comentarios = Comentario.objects.filter(ticket=ticket).order_by('fecha_creacion')

    context = {
        'view_class': 'view-tickets', # Reutilizamos estilos
        'ticket': ticket,
        'form': form,
        'comentarios': comentarios
    }
    return render(request, 'gestionar_ticket.html', context)