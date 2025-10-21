# tickets/views.py
from django.shortcuts import render, redirect
from .models import Ticket, Usuario, AsignacionTicket, Comentario, Prioridad, Categoria
from django.shortcuts import render, redirect, get_object_or_404, reverse
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
        form = AsignacionTicketForm(request.POST, ticket=ticket_para_asignar)
        if form.is_valid():
                # ---  ACTUALIZAR EL TICKET PRIMERO ---
            ticket_para_asignar.prioridad = form.cleaned_data['prioridad']
            ticket_para_asignar.categoria = form.cleaned_data['categoria']
            ticket_para_asignar.estado = 'EN_PROGRESO' # Lo asignamos aquí también
            ticket_para_asignar.save()
            # --- FIN DE ACTUALIZACIÓN DEL TICKET ---

            # Creamos la asignación (solo usuario y comentarios)
            asignacion = AsignacionTicket(
                ticket=ticket_para_asignar,
                usuario_asignado=form.cleaned_data['usuario_asignado'],
                comentarios=form.cleaned_data['comentarios']
            )
            asignacion.save()

            # La redirección se mantiene igual
            return redirect(f"{reverse('ticket_list')}?estado={estado_filtro}&orden={orden}")
        else:
            # Si el form falla, necesitamos preparar el contexto igual que en GET
            ticket_seleccionado = ticket_para_asignar
            # Pasamos el ticket para inicializar y el form con errores
            asignacion_form = form # Muestra los errores
            lista_tickets = tickets_query.all() # Necesitamos la lista aquí también

        # --- Lógica para mostrar el panel lateral (GET) ---
    else: # Si NO es POST o no tiene ticket_id
        ticket_seleccionado = None
        asignacion_form = None
        if ticket_id:
            ticket_seleccionado = get_object_or_404(Ticket, pk=ticket_id)
            # Pasamos el ticket al inicializar el formulario 
            asignacion_form = AsignacionTicketForm(ticket=ticket_seleccionado) 

        # Si no hubo POST fallido, obtenemos la lista aquí
        if request.method != 'POST':
            lista_tickets = tickets_query.all()


    context = {
        'view_class': 'view-tickets',
        'tickets': lista_tickets, 
        'ticket_seleccionado': ticket_seleccionado,
        'asignacion_form': asignacion_form, 
        'estado_actual': estado_filtro or 'todos',
        'orden_actual': orden,
        'estados_posibles': Ticket.ESTADO_CHOICES 
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
                nuevo_comentario = form_comentario_post.save(commit=False) # Prepara el objeto
                nuevo_comentario.ticket = ticket_para_comentar # Asigna el ticket
                nuevo_comentario.autor = creador # Asigna el autor (docente)
                nuevo_comentario.save() # Guarda en la BD
                # ... (guardar comentario) ...
                # Redirigimos AÑADIENDO los filtros
                return redirect(f"{reverse('mis_tickets_detalle', args=[ticket_id])}?estado={estado_filtro}&orden={orden}")
            else:
                ticket_seleccionado = ticket_para_comentar
                comentarios = Comentario.objects.filter(ticket=ticket_seleccionado).order_by('fecha_creacion')
                form_comentario = form_comentario_post # Pasa el formulario CON errores a la plantilla
        else: # Crear ticket
            form_creacion = TicketForm(request.POST) 
            if form_creacion.is_valid():
                ticket_nuevo = form_creacion.save(commit=False)
                ticket_nuevo.usuario_creador = creador
                
                # --- Asignación de Prioridad y Categoría por defecto ---
                try:
                    prioridad_media = Prioridad.objects.get(Tipo_Nivel='MEDIO')
                    ticket_nuevo.prioridad = prioridad_media
                except Prioridad.DoesNotExist:
                    prioridad_default = Prioridad.objects.first() 
                    if prioridad_default:
                        ticket_nuevo.prioridad = prioridad_default
                    else:
                        pass # Manejo de error si no hay prioridades

                try:
                    categoria_general = Categoria.objects.get(nombre='General') 
                    ticket_nuevo.categoria = categoria_general
                except Categoria.DoesNotExist:
                    categoria_default = Categoria.objects.first()
                    if categoria_default:
                         ticket_nuevo.categoria = categoria_default
                # --- Fin de Asignación por defecto ---

                ticket_nuevo.save()
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
def mis_asignaciones_view(request, ticket_id=None):
    # --- BLOQUE DE PERMISO ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'TI':
            return redirect('index')
    except Usuario.DoesNotExist:
        return redirect('index')
    # --- FIN DEL BLOQUE ---

    tecnico_actual = usuario 

    # Variables para el contexto
    ticket_seleccionado = None
    comentarios = Comentario.objects.none()
    form_gestion = None

    # --- LÓGICA POST (Solo si hay ticket_id en la URL) ---
    if request.method == 'POST' and ticket_id:
        # Buscamos el ticket que se está gestionando
        # Añadimos seguridad extra: verificamos que esté asignado a este técnico
        ticket_para_gestionar = get_object_or_404(
            Ticket, 
            pk=ticket_id, 
            asignacionticket__usuario_asignado=tecnico_actual
        )
        
        form_gestion_post = GestionTicketForm(request.POST)
        
        if form_gestion_post.is_valid():
            # 1. Actualizar estado del Ticket
            nuevo_estado = form_gestion_post.cleaned_data['estado']
            ticket_para_gestionar.estado = nuevo_estado
            if nuevo_estado in ['CERRADO', 'RESUELTO']:
                ticket_para_gestionar.cerrado_en = timezone.now().date()
            else:
                ticket_para_gestionar.cerrado_en = None
            ticket_para_gestionar.save()

            # 2. Crear nuevo comentario (si hay contenido)
            contenido_comentario = form_gestion_post.cleaned_data['contenido']
            if contenido_comentario:
                # OJO: No usamos form.save() directamente porque GestionTicketForm
                # no está basado en Comentario para todos sus campos.
                Comentario.objects.create(
                    ticket=ticket_para_gestionar,
                    autor=tecnico_actual,
                    contenido=contenido_comentario
                )
                
            # 3. Redirigir manteniendo filtros y mostrando el ticket actualizado
            estado_filtro = request.GET.get('estado', '') 
            orden = request.GET.get('orden', 'reciente')
            # Redirigimos a la vista detalle para ver el resultado
            return redirect(f"{reverse('mis_asignaciones_detalle', args=[ticket_id])}?estado={estado_filtro}&orden={orden}")
        else:
            # Si el form falla, preparamos contexto para mostrar error
            ticket_seleccionado = ticket_para_gestionar
            comentarios = Comentario.objects.filter(ticket=ticket_seleccionado).order_by('fecha_creacion')
            form_gestion = form_gestion_post # Pasa el form con errores

    # --- LÓGICA GET (y preparación de formularios) ---
    # (Filtros y ordenamiento)
    estado_filtro = request.GET.get('estado', '') 
    orden = request.GET.get('orden', 'reciente')
    tickets_query = Ticket.objects.filter(
        asignacionticket__usuario_asignado=tecnico_actual
    ).distinct()
    if estado_filtro and estado_filtro != 'todos':
        tickets_query = tickets_query.filter(estado=estado_filtro)
    if orden == 'antiguo':
        tickets_query = tickets_query.order_by('fecha_creacion')
    else: 
        tickets_query = tickets_query.order_by('-fecha_creacion')
    lista_tickets = tickets_query.select_related('usuario_creador', 'prioridad').all()

    # Si se está viendo un ticket específico (GET o POST fallido)
    if ticket_id:
        if not ticket_seleccionado: # Si no lo seteamos arriba por POST fallido
             # Aseguramos que el técnico solo vea tickets asignados a él
            ticket_seleccionado = get_object_or_404(
            Ticket,
            pk=ticket_id
            )
            comentarios = Comentario.objects.filter(ticket=ticket_seleccionado).order_by('fecha_creacion')
            form_gestion = GestionTicketForm(initial={'estado': ticket_seleccionado.estado}) # Form gestión

    context = {
        'view_class': 'view-tickets', # Usamos la clase que permite 2 columnas
        'tickets': lista_tickets,
        'view_title': 'Mis Asignaciones',
        # Datos para el panel lateral
        'ticket_seleccionado': ticket_seleccionado,
        'comentarios': comentarios,
        'form_gestion': form_gestion, # Renombrado para claridad
        # Datos para los filtros
        'estado_actual': estado_filtro or 'todos',
        'orden_actual': orden,
        'estados_posibles': Ticket.ESTADO_CHOICES
    }
    return render(request, 'mis_asignaciones.html', context)
