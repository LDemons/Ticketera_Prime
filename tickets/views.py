# tickets/views.py
from django.shortcuts import render, redirect
from .models import Ticket, Usuario, AsignacionTicket, Comentario
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required 
from .forms import TicketForm, AsignacionTicketForm, GestionTicketForm, ComentarioForm
from django.utils import timezone
from datetime import timedelta
from django.db.models import F, ExpressionWrapper, fields, Avg, Min, Func, Value

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
            return redirect('index') 
    except Usuario.DoesNotExist:
        return redirect('index') 
    # --- FIN DEL BLOQUE ---

    # ahora_dt es datetime, ahora_date es solo date
    ahora_dt = timezone.now()
    ahora_date = ahora_dt.date() # <--- Obtenemos solo la fecha actual

    # --- 1. KPI: Tickets Abiertos ---
    tickets_abiertos = Ticket.objects.filter(estado='ABIERTO').count()

    # --- 2. KPI: Tickets En Progreso ---
    tickets_en_progreso = Ticket.objects.filter(estado='EN_PROGRESO').count()

    # --- 3. KPI: SLA Vencidos (Calculado en Python) ---
    estados_activos = ['ABIERTO', 'EN_PROGRESO']
    tickets_activos = Ticket.objects.filter(
        estado__in=estados_activos
    ).select_related('prioridad')

    sla_vencidos_count = 0
    for ticket in tickets_activos:
        horas_sla = ticket.prioridad.sla_horas

        # Sumamos días basados en horas. // 24 da la parte entera de días.
        dias_sla = horas_sla // 24 
        # Calculamos la fecha de vencimiento sumando DÍAS
        # Nota: Esto es menos preciso que horas, pero compatible con DateField
        fecha_vencimiento = ticket.fecha_creacion + timedelta(days=dias_sla) 

        # Comparamos DATE con DATE
        if fecha_vencimiento < ahora_date: # <--- Usamos ahora_date
            sla_vencidos_count += 1

    # --- 4. KPI: Tiempo de Primera Respuesta (Asignación) ---
    # Como fecha_creacion y fecha_asignacion son DateFields,
    # la diferencia será en días. No podemos calcular horas/minutos fácilmente.
    # Mostraremos el promedio en días.
    tickets_con_asignacion = Ticket.objects.annotate(
        primera_asignacion=Min('asignacionticket__fecha_asignacion')
    ).filter(
        primera_asignacion__isnull=False
    ).annotate(
        # La resta de dos DateFields da un timedelta en días
        tiempo_primera_respuesta_dias=ExpressionWrapper(
            F('primera_asignacion') - F('fecha_creacion'),
            output_field=fields.DurationField() # Django lo maneja como Duration
        )
    )

    promedio_timedelta_dias = tickets_con_asignacion.aggregate(
        promedio=Avg('tiempo_primera_respuesta_dias')
    )['promedio']

    tiempo_respuesta_promedio_str = "N/A"
    if promedio_timedelta_dias:
        # Obtenemos los días del timedelta
        dias_promedio = promedio_timedelta_dias.days
        tiempo_respuesta_promedio_str = f"{dias_promedio} día(s)" # Mostramos días

    context = {
        'view_class': 'view-dashboard',
        'tickets_abiertos': tickets_abiertos,
        'tickets_en_progreso': tickets_en_progreso,
        'sla_vencidos': sla_vencidos_count,
        'tiempo_respuesta': tiempo_respuesta_promedio_str, # Ahora en días
    }
    return render(request, 'dashboard.html', context)

@login_required
def ticket_list_view(request, ticket_id=None):
    # --- BLOQUE DE PERMISO ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'Admin':
            return redirect('index')
    except Usuario.DoesNotExist:
        return redirect('index')
    # --- FIN DEL BLOQUE ---

    # --- LÓGICA DE FILTRADO Y ORDENAMIENTO ---
    estado_filtro = request.GET.get('estado', '') # '' significa 'todos'
    orden = request.GET.get('orden', 'reciente') # 'reciente' por defecto

    # Query base (todos los tickets)
    tickets_query = Ticket.objects.select_related('usuario_creador', 'prioridad')

    # Aplicar filtro de estado si se seleccionó uno
    if estado_filtro and estado_filtro != 'todos':
        tickets_query = tickets_query.filter(estado=estado_filtro)

    # Aplicar ordenamiento
    if orden == 'antiguo':
        tickets_query = tickets_query.order_by('fecha_creacion')
    else: # 'reciente' o cualquier otro valor
        tickets_query = tickets_query.order_by('-fecha_creacion')

    # Ejecutamos la consulta para obtener la lista
    lista_tickets = tickets_query.all()
    # --- FIN DE LÓGICA DE FILTRADO ---


    # Lógica de asignación (POST) - (Se mantiene igual)
    if request.method == 'POST' and ticket_id:
        ticket_para_asignar = get_object_or_404(Ticket, pk=ticket_id)
        form = AsignacionTicketForm(request.POST)
        if form.is_valid():
            asignacion = form.save(commit=False)
            asignacion.ticket = ticket_para_asignar
            asignacion.save()
            ticket_para_asignar.estado = 'EN_PROGRESO'
            ticket_para_asignar.save()
            # Redirigimos AÑADIENDO los filtros actuales para mantener la vista
            return redirect(f"{reverse('ticket_list')}?estado={estado_filtro}&orden={orden}")

    # Lógica para mostrar el panel lateral (GET) - (Se mantiene igual)
    ticket_seleccionado = None
    asignacion_form = None
    if ticket_id:
        ticket_seleccionado = get_object_or_404(Ticket, pk=ticket_id)
        asignacion_form = AsignacionTicketForm()

    context = {
        'view_class': 'view-tickets',
        'tickets': lista_tickets, # Usamos la lista filtrada/ordenada
        'ticket_seleccionado': ticket_seleccionado,
        'asignacion_form': asignacion_form,
        # Pasamos los filtros actuales al contexto para usarlos en la plantilla
        'estado_actual': estado_filtro or 'todos',
        'orden_actual': orden,
        'estados_posibles': Ticket.ESTADO_CHOICES # Pasamos los estados posibles
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
            return redirect('index')
    except Usuario.DoesNotExist:
        return redirect('index')
    # --- FIN DEL BLOQUE ---
    
    creador = usuario 

    # --- LÓGICA DE FILTRADO Y ORDENAMIENTO ---
    estado_filtro = request.GET.get('estado', '') # '' significa 'todos'
    orden = request.GET.get('orden', 'reciente') # 'reciente' por defecto

    # Query base (SOLO los tickets del docente)
    tickets_query = Ticket.objects.filter(usuario_creador=creador)

    # Aplicar filtro de estado
    if estado_filtro and estado_filtro != 'todos':
        tickets_query = tickets_query.filter(estado=estado_filtro)

    # Aplicar ordenamiento
    if orden == 'antiguo':
        tickets_query = tickets_query.order_by('fecha_creacion')
    else: 
        tickets_query = tickets_query.order_by('-fecha_creacion')

    lista_tickets = tickets_query.select_related('prioridad').all() # Ejecutamos aquí
    # --- FIN DE LÓGICA DE FILTRADO ---

    ticket_seleccionado = None
    comentarios = Comentario.objects.none()
    form_comentario = None
    
    # --- LÓGICA POST --- (Se mantiene igual, solo ajusta la redirección)
    if request.method == 'POST':
        if ticket_id: # Añadir comentario
            ticket_para_comentar = get_object_or_404(Ticket, pk=ticket_id, usuario_creador=creador)
            form_comentario_post = ComentarioForm(request.POST)
            if form_comentario_post.is_valid():
                # ... (guardar comentario) ...
                # Redirigimos AÑADIENDO los filtros
                return redirect(f"{reverse('mis_tickets_detalle', args=[ticket_id])}?estado={estado_filtro}&orden={orden}")
            else:
                ticket_seleccionado = ticket_para_comentar
                comentarios = Comentario.objects.filter(ticket=ticket_seleccionado).order_by('fecha_creacion')
                form_comentario = form_comentario_post
        else: # Crear ticket
            form_creacion = TicketForm(request.POST)
            if form_creacion.is_valid():
                # ... (guardar ticket) ...
                # Redirigimos AÑADIENDO los filtros
                return redirect(f"{reverse('mis_tickets')}?estado={estado_filtro}&orden={orden}")
    
    # --- LÓGICA GET --- (Se mantiene igual)
    form_creacion = TicketForm() 
    if ticket_id:
        if not ticket_seleccionado:
            ticket_seleccionado = get_object_or_404(Ticket, pk=ticket_id, usuario_creador=creador)
            comentarios = Comentario.objects.filter(ticket=ticket_seleccionado).order_by('fecha_creacion')
            form_comentario = ComentarioForm() 

    context = {
        'view_class': 'view-tickets', 
        'tickets': lista_tickets, # Usamos la lista filtrada/ordenada
        'form_creacion': form_creacion, 
        'ticket_seleccionado': ticket_seleccionado,
        'comentarios': comentarios,
        'form_comentario': form_comentario,
        # Pasamos filtros al contexto
        'estado_actual': estado_filtro or 'todos',
        'orden_actual': orden,
        'estados_posibles': Ticket.ESTADO_CHOICES
    }
    return render(request, 'mis_tickets.html', context)




@login_required
def mis_asignaciones_view(request):
    # --- BLOQUE DE PERMISO ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'TI':
            return redirect('index')
    except Usuario.DoesNotExist:
        return redirect('index')
    # --- FIN DEL BLOQUE ---

    tecnico_actual = usuario 

    # --- LÓGICA DE FILTRADO Y ORDENAMIENTO ---
    estado_filtro = request.GET.get('estado', '') # '' significa 'todos'
    orden = request.GET.get('orden', 'reciente') # 'reciente' por defecto

    # Query base (SOLO tickets asignados al técnico)
    tickets_query = Ticket.objects.filter(
        asignacionticket__usuario_asignado=tecnico_actual
    ).distinct() # Distinct es importante si un ticket se reasigna

    # Aplicar filtro de estado
    if estado_filtro and estado_filtro != 'todos':
        tickets_query = tickets_query.filter(estado=estado_filtro)

    # Aplicar ordenamiento
    if orden == 'antiguo':
        tickets_query = tickets_query.order_by('fecha_creacion')
    else: 
        tickets_query = tickets_query.order_by('-fecha_creacion')

    lista_tickets = tickets_query.select_related('usuario_creador', 'prioridad').all()
    # --- FIN DE LÓGICA DE FILTRADO ---

    context = {
        'view_class': 'view-tickets', 
        'tickets': lista_tickets, # Usamos la lista filtrada/ordenada
        'view_title': 'Mis Asignaciones',
        # Pasamos filtros al contexto
        'estado_actual': estado_filtro or 'todos',
        'orden_actual': orden,
        'estados_posibles': Ticket.ESTADO_CHOICES
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

    # --- LÓGICA POST ---
    if request.method == 'POST':
        form = GestionTicketForm(request.POST)
        if form.is_valid():
            # 1. Actualizar el estado del Ticket
            nuevo_estado = form.cleaned_data['estado']
            ticket.estado = nuevo_estado

            # Si el estado es 'CERRADO' o 'RESUELTO', guardamos la fecha
            # (Ajustado para DateField, solo guarda la fecha actual)
            if nuevo_estado in ['CERRADO', 'RESUELTO']:
                 # Usamos timezone.now().date() para obtener solo la fecha
                ticket.cerrado_en = timezone.now().date()
            else:
                 # Si se reabre, quitamos la fecha de cierre
                ticket.cerrado_en = None 

            ticket.save()

            # 2. Crear el nuevo comentario
            contenido_comentario = form.cleaned_data['contenido']
            if contenido_comentario: # Solo si el técnico escribió algo
                nuevo_comentario = form.save(commit=False)
                nuevo_comentario.ticket = ticket
                nuevo_comentario.autor = tecnico_actual
                nuevo_comentario.save()

            # 3. Redirigir de vuelta a la lista de asignaciones
            #    Leemos los filtros de la URL actual para mantenerlos
            estado_filtro = request.GET.get('estado', '') 
            orden = request.GET.get('orden', 'reciente')
            return redirect(f"{reverse('mis_asignaciones')}?estado={estado_filtro}&orden={orden}")
            
    # --- LÓGICA GET ---
    else:
        # Si es GET, mostramos el formulario con el estado actual del ticket
        form = GestionTicketForm(initial={'estado': ticket.estado})

    # Obtenemos todos los comentarios existentes para este ticket
    comentarios = Comentario.objects.filter(ticket=ticket).order_by('fecha_creacion')

    context = {
        'view_class': 'view-tickets', # Reutilizamos estilos
        'ticket': ticket,
        'form': form,
        'comentarios': comentarios,
        # Pasamos los filtros actuales para que el enlace "Volver" funcione
        'estado_actual': request.GET.get('estado', 'todos'),
        'orden_actual': request.GET.get('orden', 'reciente'),
    }
    return render(request, 'gestionar_ticket.html', context)