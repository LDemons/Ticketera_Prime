# tickets/views.py
from django.shortcuts import render, redirect
from .models import Ticket, Usuario
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required 
from .forms import TicketForm


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
    tickets = Ticket.objects.select_related('usuario_creador', 'prioridad').all()
    
    ticket_seleccionado = None
    if ticket_id:
        # Busca el ticket para mostrarlo en el panel lateral
        ticket_seleccionado = get_object_or_404(Ticket, pk=ticket_id)

    print(f"ID de ticket recibido: {ticket_id}, Ticket seleccionado: {ticket_seleccionado}")

    context = {
        'view_class': 'view-tickets',
        'tickets': tickets,
        'ticket_seleccionado': ticket_seleccionado
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

@login_required # 👈 Protege la vista
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