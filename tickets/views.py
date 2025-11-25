from django.shortcuts import render, redirect
from .models import Ticket, Usuario, AsignacionTicket, Comentario, Prioridad, Categoria, Notificacion
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required 
from .forms import TicketForm, AsignacionTicketForm, GestionTicketForm, ComentarioForm
from django.utils import timezone
import json
from datetime import timedelta, date, datetime
from django.db.models import F, ExpressionWrapper, fields, Avg, Min, Func, Value, Count
from django.views.decorators.http import require_POST


@login_required
def landing_view(request):
    """
    Muestra una página de bienvenida con opciones según el rol.
    """
    usuario_app = None # Variable para nuestro modelo Usuario
    try:
        # Buscamos el usuario de nuestro modelo basado en el usuario de Django
        usuario_app = Usuario.objects.get(email=request.user.email)
    except Usuario.DoesNotExist:
        # Si no existe en nuestro modelo, puede ser un superuser de Django
        if not request.user.is_superuser:
            # Si no es superuser y no existe, algo anda mal, lo sacamos.
             return redirect('login') 
             # O podrías mostrar un mensaje de error en landing.html si prefieres

    context = {
        # Pasamos el usuario de nuestra app (si existe) para los 'if' de rol
        'usuario': usuario_app, 
        # Podemos usar una clase diferente si queremos estilos específicos
        'view_class': 'view-landing' 
    }
    return render(request, 'landing.html', context)

@login_required
def index_view(request):
    """
    Redirige SIEMPRE a la página de bienvenida después del login.
    La vista 'landing_view' se encargará de mostrar lo correcto.
    """
    # Verificamos si el usuario logueado existe en nuestro modelo Usuario
    # o si es un superuser de Django. Si no, lo mandamos al login.
    # (Esto es una seguridad extra por si acaso)
    try:
        Usuario.objects.get(email=request.user.email)
        # Si existe, lo mandamos a la landing page
        return redirect('landing_page') 
    except Usuario.DoesNotExist:
        # Si no existe, vemos si es superuser de Django
        if request.user.is_superuser:
            # El superuser también va a la landing page (ella decidirá qué mostrar)
             return redirect('landing_page')
        else:
            # Si no es superuser y no existe en Usuario, algo raro pasa, al login.
            return redirect('login')


@login_required
def dashboard_view(request):
    """
    Vista de Dashboard con gráficos analíticos.
    """
    # --- BLOQUE DE PERMISO (Solo Admin) ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'Admin':
            return redirect('index')
    except Usuario.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('index')
    # --- FIN DEL BLOQUE ---

    ahora_date = timezone.now().date()

    # 1. Gráfico de Tickets por Estado (Pie)
    conteo_por_estado = Ticket.objects.values('estado').annotate(
        total=Count('ticket_id')
    ).order_by('estado')
    
    mapa_estados = dict(Ticket.ESTADO_CHOICES)
    labels_estado = [mapa_estados.get(item['estado'], item['estado']) for item in conteo_por_estado]
    data_estado = [item['total'] for item in conteo_por_estado]

    # 2. Gráfico de Tickets por Categoría (Barras)
    conteo_por_categoria = Ticket.objects.values('categoria__nombre').annotate(
        total=Count('ticket_id')
    ).order_by('categoria__nombre')
    
    labels_categoria = [item['categoria__nombre'] if item['categoria__nombre'] else 'Sin categoría' for item in conteo_por_categoria]
    data_categoria = [item['total'] for item in conteo_por_categoria]

    # 3. Tickets Creados por Día (Últimos 7 Días)
    fechas_ultimos_7_dias = [ahora_date - timedelta(days=i) for i in range(7)]
    fechas_ultimos_7_dias.reverse()

    dias_semana_map = {
        'Sun': 'Dom', 'Mon': 'Lun', 'Tue': 'Mar', 'Wed': 'Mié',
        'Thu': 'Jue', 'Fri': 'Vie', 'Sat': 'Sáb'
    }

    labels_creados_dia = []
    data_creados_dia = []

    for d in fechas_ultimos_7_dias:
        dia_semana_es = d.strftime('%a')
        dia_semana_es = dias_semana_map.get(dia_semana_es, dia_semana_es)
        labels_creados_dia.append(dia_semana_es)
        
        count_for_day = Ticket.objects.filter(fecha_creacion__date=d).count()
        data_creados_dia.append(count_for_day)

    # 4. Tickets Abiertos por Prioridad
    conteo_por_prioridad = Ticket.objects.filter(
        estado__in=['ABIERTO', 'EN_PROGRESO']
    ).values('prioridad__Tipo_Nivel').annotate(
        total=Count('ticket_id')
    ).order_by('prioridad__Tipo_Nivel')

    mapa_prioridad = dict(Prioridad.NIVEL_CHOICES)
    labels_prioridad = [
        mapa_prioridad.get(item['prioridad__Tipo_Nivel'], item['prioridad__Tipo_Nivel'])
        for item in conteo_por_prioridad
    ]
    data_prioridad = [item['total'] for item in conteo_por_prioridad]

    context = {
        'view_class': 'view-dashboard',
        'labels_estado_json': json.dumps(labels_estado),
        'data_estado_json': json.dumps(data_estado),
        'labels_categoria_json': json.dumps(labels_categoria),
        'data_categoria_json': json.dumps(data_categoria),
        'labels_creados_dia_json': json.dumps(labels_creados_dia),
        'data_creados_dia_json': json.dumps(data_creados_dia),
        'labels_prioridad_json': json.dumps(labels_prioridad),
        'data_prioridad_json': json.dumps(data_prioridad),
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
    estado_filtro = request.GET.get('estado', '')
    orden = request.GET.get('orden', 'reciente')

    tickets_query = Ticket.objects.select_related('usuario_creador', 'prioridad')

    if estado_filtro and estado_filtro != 'todos':
        tickets_query = tickets_query.filter(estado=estado_filtro)

    if orden == 'antiguo':
        tickets_query = tickets_query.order_by('fecha_creacion')
    else:
        tickets_query = tickets_query.order_by('-fecha_creacion')

    lista_tickets = tickets_query.all()
    # --- FIN DE LÓGICA DE FILTRADO ---

    # Lógica de asignación (POST)
    if request.method == 'POST' and ticket_id:
        ticket_para_asignar = get_object_or_404(Ticket, pk=ticket_id)
        form = AsignacionTicketForm(request.POST, ticket=ticket_para_asignar)
        if form.is_valid():
            # Actualizar el ticket
            ticket_para_asignar.prioridad = form.cleaned_data['prioridad']
            ticket_para_asignar.categoria = form.cleaned_data['categoria']
            ticket_para_asignar.estado = 'EN_PROGRESO'
            ticket_para_asignar.save()

            # Crear la asignación (con comentarios incluidos)
            asignacion = AsignacionTicket(
                ticket=ticket_para_asignar,
                usuario_asignado=form.cleaned_data['usuario_asignado'],
                comentarios=form.cleaned_data['comentarios'] or ''  # Se guarda en la asignación
            )
            asignacion.save()

            # ELIMINADO: Ya NO creamos un Comentario aquí
            # El signal de AsignacionTicket se encargará de crear la notificación
            # con el mensaje del admin incluido

            return redirect(f"{reverse('ticket_list')}?estado={estado_filtro}&orden={orden}")
        else:
            ticket_seleccionado = ticket_para_asignar
            asignacion_form = form
            lista_tickets = tickets_query.all()
    else:
        ticket_seleccionado = None
        asignacion_form = None
        if ticket_id:
            ticket_seleccionado = get_object_or_404(Ticket, pk=ticket_id)
            asignacion_form = AsignacionTicketForm(ticket=ticket_seleccionado)

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
                
                # --- NO asignamos prioridad ni categoría ---
                # Esto lo hará el Admin al asignar el ticket
                # prioridad y categoria quedan como None (null en BD)

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


# --- VISTA PARA BORRAR (DOCENTE) ---
@require_POST # Solo permite peticiones POST
@login_required
def borrar_mi_ticket_view(request, ticket_id):
    # --- BLOQUE DE PERMISO ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'Docente':
            # Si no es Docente, no puede borrar "sus" tickets
            # Podríamos redirigir a 'index' o mostrar error 403 (Prohibido)
            return redirect('index') 
    except Usuario.DoesNotExist:
        return redirect('index') 
    # --- FIN DEL BLOQUE ---

    # Busca el ticket asegurándose que pertenece al usuario logueado
    ticket_a_borrar = get_object_or_404(Ticket, pk=ticket_id, usuario_creador=usuario)
    
    # Borra el ticket
    ticket_a_borrar.delete()
    
    # Redirige de vuelta a la lista "Mis Tickets" (manteniendo filtros si existen)
    estado_filtro = request.GET.get('estado', '') 
    orden = request.GET.get('orden', 'reciente')
    return redirect(f"{reverse('mis_tickets')}?estado={estado_filtro}&orden={orden}")


# --- VISTA PARA BORRAR (ADMIN) ---
@require_POST # Solo permite peticiones POST
@login_required
def borrar_ticket_admin_view(request, ticket_id):
    # --- BLOQUE DE PERMISO ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'Admin':
            # Si no es Admin, no puede borrar tickets
            return redirect('index') 
    except Usuario.DoesNotExist:
        # Superuser de Django sin Usuario en app? Permitir o redirigir
        if not request.user.is_superuser:
            return redirect('index')
    # --- FIN DEL BLOQUE ---

    # El Admin puede borrar cualquier ticket, solo busca por ID
    ticket_a_borrar = get_object_or_404(Ticket, pk=ticket_id)
    
    # Borra el ticket
    ticket_a_borrar.delete()
    
    # Redirige de vuelta a la lista general "Tickets" (manteniendo filtros)
    estado_filtro = request.GET.get('estado', '') 
    orden = request.GET.get('orden', 'reciente')
    return redirect(f"{reverse('ticket_list')}?estado={estado_filtro}&orden={orden}")

@login_required
def reportes_view(request):
    # --- BLOQUE DE PERMISO (Solo Admin) ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'Admin':
            return redirect('index') 
    except Usuario.DoesNotExist:
        if not request.user.is_superuser:
             return redirect('index')
    # --- FIN DEL BLOQUE ---

    # 1. Reporte: Conteo de Tickets por Estado
    conteo_por_estado = Ticket.objects.values('estado').annotate(
        total=Count('ticket_id')
    ).order_by('estado')

    reporte_estados = []
    for item in conteo_por_estado:
        temp_ticket = Ticket(estado=item['estado']) 
        reporte_estados.append({
            'estado': temp_ticket.get_estado_display(), 
            'total': item['total']
        })

    # 2. Reporte: Conteo de Tickets por Categoría
    conteo_por_categoria = Ticket.objects.values('categoria__nombre').annotate(
        total=Count('ticket_id')
    ).order_by('categoria__nombre')

    reporte_categorias = [
        {'categoria': item['categoria__nombre'], 'total': item['total']}
        for item in conteo_por_categoria
    ]

    context = {
        'view_class': 'view-reportes', 
        'reporte_estados': reporte_estados,
        'reporte_categorias': reporte_categorias,
    }
    return render(request, 'reportes.html', context)

@login_required
def reportes_view(request):
    # --- BLOQUE DE PERMISO (Solo Admin) ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'Admin':
            return redirect('index')
    except Usuario.DoesNotExist:
        if not request.user.is_superuser:
             return redirect('index')
    # --- FIN DEL BLOQUE ---

    # --- 👇 PROCESAMIENTO DE FECHAS 👇 ---
    fecha_desde_str = request.GET.get('fecha_desde', '')
    fecha_hasta_str = request.GET.get('fecha_hasta', '')

    fecha_desde = None
    fecha_hasta = None

    # Convertir strings a objetos date (si son válidos)
    try:
        if fecha_desde_str:
            fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d').date()
    except ValueError:
        fecha_desde = None # Ignora fecha inválida

    try:
        if fecha_hasta_str:
            # Sumamos un día y usamos '<' para incluir el día 'hasta' completo
            fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date()
    except ValueError:
        fecha_hasta = None # Ignora fecha inválida

    # --- FIN PROCESAMIENTO DE FECHAS ---

    # --- Query base con filtro de fecha aplicado ---
    base_query = Ticket.objects.all() # Empezamos con todos los tickets

    # Aplicar filtros de fecha si existen
    if fecha_desde and fecha_hasta:
        # Si tenemos ambas, filtramos por rango (__range)
        base_query = base_query.filter(fecha_creacion__range=(fecha_desde, fecha_hasta))
    elif fecha_desde:
        # Si solo hay 'desde', filtramos desde esa fecha en adelante (__gte)
        base_query = base_query.filter(fecha_creacion__gte=fecha_desde)
    elif fecha_hasta:
        # Si solo hay 'hasta', filtramos hasta esa fecha inclusive (__lte)
         base_query = base_query.filter(fecha_creacion__lte=fecha_hasta)

    # --- FIN Query base ---

    # 1. Reporte: Conteo de Tickets por Estado
    conteo_por_estado = base_query.values('estado').annotate(
        total=Count('ticket_id')
    ).order_by('estado')

    reporte_estados = []
    for item in conteo_por_estado:
        # Usamos .get() con default por si el estado no está en CHOICES (poco probable)
        estado_display = dict(Ticket.ESTADO_CHOICES).get(item['estado'], item['estado'])
        reporte_estados.append({
            'estado': estado_display, # Nombre legible
            'total': item['total']
        })

    # 2. Reporte: Conteo de Tickets por Categoría
    conteo_por_categoria = base_query.values('categoria__nombre').annotate(
        total=Count('ticket_id')
    ).order_by('categoria__nombre')

    reporte_categorias = [
        # Aseguramos que si una categoría es None (si permitieras null), se muestre como 'Sin categoría'
        {'categoria': item['categoria__nombre'] if item['categoria__nombre'] else 'Sin categoría', 'total': item['total']}
        for item in conteo_por_categoria
    ]

    conteo_por_prioridad = base_query.values('prioridad__Tipo_Nivel').annotate(
        total=Count('ticket_id')
    ).order_by('prioridad__Tipo_Nivel') # Ordena por ALTO, BAJO, MEDIO

    # Mapeamos los códigos ('ALTO', 'BAJO', 'MEDIO') a nombres legibles
    # Usamos los NIVEL_CHOICES definidos en el modelo Prioridad
    prioridad_map = dict(Prioridad.NIVEL_CHOICES) 
    reporte_prioridades = [
        {'prioridad': prioridad_map.get(item['prioridad__Tipo_Nivel'], 'Desconocida'), 
         'total': item['total']}
        for item in conteo_por_prioridad
    ]

    context = {
        'view_class': 'view-dashboard', # Clase para CSS específico si es necesario
        'reporte_estados': reporte_estados,
        'reporte_categorias': reporte_categorias,
        'reporte_prioridades': reporte_prioridades,
        'fecha_desde_str': fecha_desde_str,
        'fecha_hasta_str': fecha_hasta_str,
    }
    return render(request, 'reportes.html', context)

@login_required
def notificaciones_view(request):
    """
    Muestra la lista de notificaciones del usuario y las marca como leídas.
    """
    try:
        # Buscamos nuestro modelo de Usuario
        usuario_app = Usuario.objects.get(email=request.user.email)
    except Usuario.DoesNotExist:
        # Si no existe (p.ej. Superuser), redirigir
        return redirect('index')

    # 1. Obtenemos todas las notificaciones del usuario (leídas y no leídas)
    notificaciones_list = Notificacion.objects.filter(usuario_destino=usuario_app)

    # 2. Obtenemos las no leídas (antes de renderizar) para marcarlas
    notificaciones_no_leidas = notificaciones_list.filter(leido=False)
    
    # 3. Marcamos todas las no leídas como leídas
    # Usamos .update() que es más eficiente que iterar y guardar
    notificaciones_no_leidas.update(leido=True)

    context = {
        'view_class': 'view-dashboard', # Reutilizamos esta clase para el layout
        'notificaciones': notificaciones_list,
        'usuario_rol': usuario_app.rol.nombre
    }
    
    return render(request, 'notificaciones.html', context)

@login_required
def panel_principal_view(request):
    """
    Vista del Panel Principal con KPIs y vistas resumidas (sin gráficos).
    """
    # --- BLOQUE DE PERMISO (Solo Admin) ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'Admin':
            return redirect('index')
    except Usuario.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('index')
    # --- FIN DEL BLOQUE ---

    ahora_dt = timezone.now()
    ahora_date = ahora_dt.date()

    # --- KPIs ---
    tickets_abiertos = Ticket.objects.filter(estado='ABIERTO').count()
    tickets_en_progreso = Ticket.objects.filter(estado='EN_PROGRESO').count()
    
    # --- SLA Vencidos ---
    estados_activos = ['ABIERTO', 'EN_PROGRESO']
    tickets_activos = Ticket.objects.filter(
        estado__in=estados_activos,
        prioridad__isnull=False  # Solo tickets con prioridad asignada
    ).select_related('prioridad')
    
    sla_vencidos_count = 0
    for ticket in tickets_activos:
        horas_sla = ticket.prioridad.sla_horas
        if horas_sla > 0:
            fecha_vencimiento = ticket.fecha_creacion + timedelta(hours=horas_sla)
            if fecha_vencimiento < ahora_dt:
                sla_vencidos_count += 1

    # --- Tiempo de Respuesta Promedio ---
    tickets_con_asignacion = Ticket.objects.annotate(
        primera_asignacion=Min('asignacionticket__fecha_asignacion')
    ).filter(primera_asignacion__isnull=False)

    diferencia_de_tiempo = tickets_con_asignacion.annotate(
        tiempo_diff=ExpressionWrapper(
            F('primera_asignacion') - F('fecha_creacion'),
            output_field=fields.DurationField()
        )
    )

    promedio_timedelta = diferencia_de_tiempo.aggregate(
        promedio=Avg('tiempo_diff')
    )['promedio']

    tiempo_respuesta_promedio_str = "N/A"
    if promedio_timedelta:
        total_minutos = promedio_timedelta.total_seconds() / 60
        if total_minutos < 60:
            tiempo_respuesta_promedio_str = f"{total_minutos:.0f}m"
        else:
            total_horas = total_minutos / 60
            tiempo_respuesta_promedio_str = f"{total_horas:.1f}h"

    # --- Variaciones de últimas 24h ---
    hace_24h = ahora_dt - timedelta(hours=24)
    
    abiertos_ultimas_24h = Ticket.objects.filter(
        estado='ABIERTO',
        fecha_creacion__gte=hace_24h
    ).count()
    
    asignaciones_ultimas_24h = AsignacionTicket.objects.filter(
        fecha_asignacion__gte=hace_24h
    ).count()
    
    asignados_hoy = AsignacionTicket.objects.filter(
        fecha_asignacion__date=ahora_date
    ).count()

    # --- Tickets Recientes (Mi Cola) ---
    tickets_recientes = Ticket.objects.filter(
        estado='ABIERTO'
    ).select_related('usuario_creador', 'prioridad').order_by('-fecha_creacion')[:10]

    # --- NUEVO: Tickets organizados por estado para Kanban ---
    tickets_kanban = {
        'ABIERTO': Ticket.objects.filter(estado='ABIERTO').select_related('usuario_creador', 'prioridad').order_by('-fecha_creacion')[:20],
        'EN_PROGRESO': Ticket.objects.filter(estado='EN_PROGRESO').select_related('usuario_creador', 'prioridad').order_by('-fecha_creacion')[:20],
        'RESUELTO': Ticket.objects.filter(estado='RESUELTO').select_related('usuario_creador', 'prioridad').order_by('-fecha_creacion')[:20],
        'CERRADO': Ticket.objects.filter(estado='CERRADO').select_related('usuario_creador', 'prioridad').order_by('-fecha_creacion')[:20],
    }

    # --- Entradas por Hora ---
    tickets_por_hora = []
    labels_horas = []
    
    for hora in range(24):
        inicio_hora = ahora_dt.replace(hour=hora, minute=0, second=0, microsecond=0)
        fin_hora = inicio_hora + timedelta(hours=1)
        
        count = Ticket.objects.filter(
            fecha_creacion__gte=inicio_hora,
            fecha_creacion__lt=fin_hora,
            fecha_creacion__date=ahora_date
        ).count()
        
        tickets_por_hora.append(count)
        labels_horas.append(f"{hora:02d}h")

    # --- Cumplimiento SLA por Prioridad ---
    prioridades = Prioridad.objects.all()
    cumplimiento_sla = []
    
    for prioridad in prioridades:
        tickets_prioridad = Ticket.objects.filter(
            prioridad=prioridad,
            estado__in=['CERRADO', 'RESUELTO']
        ).select_related('prioridad')
        
        total = tickets_prioridad.count()
        if total == 0:
            cumplimiento_sla.append({
                'nivel': prioridad.Tipo_Nivel,
                'porcentaje': 0
            })
            continue
            
        cumplidos = 0
        for ticket in tickets_prioridad:
            if ticket.cerrado_en and prioridad.sla_horas > 0:
                fecha_cierre_dt = timezone.datetime.combine(ticket.cerrado_en, timezone.datetime.min.time())
                fecha_cierre_dt = timezone.make_aware(fecha_cierre_dt)
                tiempo_resolucion = fecha_cierre_dt - ticket.fecha_creacion
                horas_resolucion = tiempo_resolucion.total_seconds() / 3600
                if horas_resolucion <= prioridad.sla_horas:
                    cumplidos += 1
        
        porcentaje = int((cumplidos / total) * 100) if total > 0 else 0
        cumplimiento_sla.append({
            'nivel': dict(Prioridad.NIVEL_CHOICES).get(prioridad.Tipo_Nivel, prioridad.Tipo_Nivel),
            'porcentaje': porcentaje
        })

    context = {
        'view_class': 'view-panel-principal',
        # KPIs principales
        'tickets_abiertos': tickets_abiertos,
        'tickets_en_progreso': tickets_en_progreso,
        'sla_vencidos': sla_vencidos_count,
        'tiempo_respuesta': tiempo_respuesta_promedio_str,
        # Variaciones
        'abiertos_variacion': abiertos_ultimas_24h,
        'en_progreso_variacion': asignaciones_ultimas_24h,
        'sla_vencidos_variacion': 3,
        # Datos para gráficos
        'labels_horas_json': json.dumps(labels_horas),
        'tickets_por_hora_json': json.dumps(tickets_por_hora),
        # Datos para tablas
        'tickets_recientes': tickets_recientes,
        'tickets_kanban': tickets_kanban,  # <- NUEVO
        'cumplimiento_sla': cumplimiento_sla,
    }
    return render(request, 'panel_principal.html', context)