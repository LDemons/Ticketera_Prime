# tickets/views.py
from django.shortcuts import render
from .models import Ticket # 👈 ¡Importa el modelo Ticket!

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