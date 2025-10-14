# tickets/views.py
from django.shortcuts import render, redirect
from .models import Ticket, Usuario
from django.shortcuts import get_object_or_404
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

def ticket_list_view(request):
    # Obtenemos todos los tickets.
    # .select_related() optimiza la consulta para cargar los datos del usuario y prioridad
    # en la misma consulta a la base de datos, lo que es más eficiente.
    tickets = Ticket.objects.select_related('usuario_creador', 'prioridad').all()

    context = {
        'view_class': 'view-tickets', # Usamos la clase del CSS para la vista de tickets
        'tickets': tickets
    }
    return render(request, 'tickets_list.html', context)

def ticket_detail_view(request, ticket_id):
    # Busca el ticket por su ID. Si no lo encuentra, muestra un error 404.
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    context = {
        'view_class': 'view-tickets', # Mantenemos el estilo de la vista de tickets
        'ticket': ticket
    }
    return render(request, 'ticket_detail.html', context)

def mis_tickets_view(request):
    # --- SIMULACIÓN DE USUARIO CONECTADO ---
    # Como no hay login, elegimos manualmente el primer usuario de la BD.
    # Cuando implementes el login, esta línea se cambiará por el usuario real.
    usuario_simulado = Usuario.objects.first()
    # -----------------------------------------

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            # Creamos el ticket pero no lo guardamos aún en la BD
            ticket_nuevo = form.save(commit=False)
            # Le asignamos el usuario simulado como el creador
            ticket_nuevo.usuario_creador = usuario_simulado
            # Ahora sí, lo guardamos
            ticket_nuevo.save()
            return redirect('mis_tickets') # Redirigimos a la misma página
    else:
        form = TicketForm()

    # Obtenemos solo los tickets creados por nuestro usuario simulado
    tickets_del_usuario = Ticket.objects.filter(usuario_creador=usuario_simulado).order_by('-fecha_creacion')

    context = {
        'view_class': 'view-tickets',
        'tickets': tickets_del_usuario,
        'form': form,
        'usuario': usuario_simulado
    }
    return render(request, 'mis_tickets.html', context)