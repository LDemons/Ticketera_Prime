from django.shortcuts import render, redirect
from .models import Ticket, Usuario, AsignacionTicket, Comentario, Prioridad, Categoria, Notificacion, Rol
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required 
from .forms import TicketForm, AsignacionTicketForm, GestionTicketForm, ComentarioForm, UsuarioForm, CambiarContraseniaForm
from django.utils import timezone
import json
from datetime import timedelta, date, datetime
from django.db.models import F, ExpressionWrapper, fields, Avg, Min, Func, Value, Count
from django.views.decorators.http import require_POST
from .utils import is_mobile_device
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
import json


# @login_required
# def landing_view(request):
#     """
#     Muestra una página de bienvenida con opciones según el rol.
#     FUNCIÓN ELIMINADA: Ahora index_view redirecciona directamente según el rol.
#     """
#     usuario_app = None # Variable para nuestro modelo Usuario
#     try:
#         # Buscamos el usuario de nuestro modelo basado en el usuario de Django
#         usuario_app = Usuario.objects.get(email=request.user.email)
#     except Usuario.DoesNotExist:
#         # Si no existe en nuestro modelo, puede ser un superuser de Django
#         if not request.user.is_superuser:
#             # Si no es superuser y no existe, algo anda mal, lo sacamos.
#              return redirect('login') 
#              # O podrías mostrar un mensaje de error en landing.html si prefieres
# 
#     context = {
#         # Pasamos el usuario de nuestra app (si existe) para los 'if' de rol
#         'usuario': usuario_app, 
#         # Podemos usar una clase diferente si queremos estilos específicos
#         'view_class': 'view-landing' 
#     }
#     return render(request, 'landing.html', context)

@login_required
def index_view(request):
    """
    Redirige a la vista principal según el rol del usuario.
    """
    try:
        usuario_app = Usuario.objects.get(email=request.user.email)
        
        # Redirigir según el rol
        if usuario_app.rol.nombre == 'Docente':
            return redirect('mis_tickets')
        elif usuario_app.rol.nombre == 'TI':
            return redirect('mis_asignaciones')
        elif usuario_app.rol.nombre == 'Admin':
            return redirect('panel_principal')
        elif usuario_app.rol.nombre == 'Superadmin':
            return redirect('usuarios_list')
        else:
            # Rol no reconocido, mostrar error o redirigir al login
            return redirect('login')
            
    except Usuario.DoesNotExist:
        # Si es un superuser de Django sin registro en Usuario
        if request.user.is_superuser:
            return redirect('usuarios_list')  # O al admin de Django: '/admin/'
        else:
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
        if usuario.rol.nombre not in ['Admin', 'Superadmin']:
            return redirect('index')
    except Usuario.DoesNotExist:
        return redirect('index')
    # --- FIN DEL BLOQUE ---

    # --- LÓGICA DE FILTRADO Y ORDENAMIENTO ---
    estado_filtro = request.GET.get('estado', '')
    orden = request.GET.get('orden', 'reciente')

    tickets_query = Ticket.objects.select_related('usuario_creador', 'prioridad')

    # Si no hay filtro explícito, mostrar solo ABIERTOS por defecto
    if not estado_filtro or estado_filtro == 'todos':
        # Si es la primera visita (sin parámetros GET), filtrar por ABIERTO
        if not request.GET:
            tickets_query = tickets_query.filter(estado='ABIERTO')
            estado_filtro = 'ABIERTO'  # Actualizar la variable para el contexto
        elif estado_filtro == 'todos':
            # Si explícitamente seleccionó "todos", mostrar todos
            pass
    else:
        # Si hay un filtro específico, aplicarlo
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
def ticket_detail_full_view(request, ticket_id):
    """Vista para mostrar el detalle completo del ticket en móvil (Admin)"""
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre not in ['Admin', 'Superadmin']:
            return redirect('index')
    except Usuario.DoesNotExist:
        return redirect('index')

    ticket_seleccionado = get_object_or_404(Ticket, pk=ticket_id)
    
    # Procesar POST (asignación del ticket)
    if request.method == 'POST':
        form = AsignacionTicketForm(request.POST, ticket=ticket_seleccionado)
        if form.is_valid():
            ticket_seleccionado.prioridad = form.cleaned_data['prioridad']
            ticket_seleccionado.categoria = form.cleaned_data['categoria']
            ticket_seleccionado.estado = 'EN_PROGRESO'
            ticket_seleccionado.save()

            asignacion = AsignacionTicket(
                ticket=ticket_seleccionado,
                usuario_asignado=form.cleaned_data['usuario_asignado'],
                comentarios=form.cleaned_data['comentarios'] or ''
            )
            asignacion.save()

            estado_filtro = request.GET.get('estado', 'todos')
            orden = request.GET.get('orden', 'reciente')
            return redirect(f"{reverse('ticket_detail_full', args=[ticket_id])}?estado={estado_filtro}&orden={orden}")
    else:
        form = AsignacionTicketForm(ticket=ticket_seleccionado)
    
    context = {
        'ticket_seleccionado': ticket_seleccionado,
        'asignacion_form': form,
        'estado_actual': request.GET.get('estado', 'todos'),
        'orden_actual': request.GET.get('orden', 'reciente'),
    }
    
    return render(request, 'ticket_detail_full.html', context)

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
                ticket_nuevo.estado = 'ABIERTO'
                # El formulario ya asigna categoría y prioridad por defecto en su método save()
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
    
    # Siempre renderizar mis_tickets.html (tiene el panel lateral en desktop y funciona en mobile)
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
            
            # Si el ticket se marca como RESUELTO o CERRADO, se desf ija automáticamente
            if nuevo_estado in ['CERRADO', 'RESUELTO']:
                ticket_para_gestionar.cerrado_en = timezone.now().date()
                ticket_para_gestionar.fijado = False  # DESFIJAR AUTOMÁTICAMENTE
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
        tickets_query = tickets_query.order_by('-fijado', 'fecha_creacion')  # Fijados primero, luego antiguos
    else: 
        tickets_query = tickets_query.order_by('-fijado', '-fecha_creacion')  # Fijados primero, luego recientes
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
    
    # Siempre renderizar mis_asignaciones.html (tiene el panel lateral en desktop y funciona en mobile)
    return render(request, 'mis_asignaciones.html', context)


@login_required
def mis_asignaciones_detalle_view(request, ticket_id):
    """Vista para mostrar el detalle completo del ticket en móvil (TI)"""
    # Si es PC, redirigir a la vista desktop con panel lateral
    if not is_mobile_device(request):
        estado = request.GET.get('estado', 'todos')
        orden = request.GET.get('orden', 'reciente')
        return redirect(f"{reverse('mis_asignaciones', args=[ticket_id])}?estado={estado}&orden={orden}")
    
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'TI':
            return redirect('index')
    except Usuario.DoesNotExist:
        return redirect('index')

    tecnico_actual = usuario
    ticket_seleccionado = get_object_or_404(Ticket, pk=ticket_id)
    
    # Procesar POST (gestión del ticket)
    if request.method == 'POST':
        form_gestion = GestionTicketForm(request.POST)
        if form_gestion.is_valid():
            nuevo_estado = form_gestion.cleaned_data['estado']
            ticket_seleccionado.estado = nuevo_estado
            ticket_seleccionado.save()
            
            comentario_texto = form_gestion.cleaned_data['comentario']
            if comentario_texto:
                Comentario.objects.create(
                    ticket=ticket_seleccionado,
                    autor=usuario,
                    texto=comentario_texto
                )
            
            estado_filtro = request.GET.get('estado', 'todos')
            orden = request.GET.get('orden', 'reciente')
            return redirect(f"{reverse('mis_asignaciones_detalle', args=[ticket_id])}?estado={estado_filtro}&orden={orden}")
    else:
        form_gestion = GestionTicketForm(initial={'estado': ticket_seleccionado.estado})
    
    comentarios = Comentario.objects.filter(ticket=ticket_seleccionado).order_by('fecha_creacion')
    
    context = {
        'ticket_seleccionado': ticket_seleccionado,
        'comentarios': comentarios,
        'form_gestion': form_gestion,
        'estado_actual': request.GET.get('estado', 'todos'),
        'orden_actual': request.GET.get('orden', 'reciente'),
    }
    
    return render(request, 'mis_asignaciones_detalle.html', context)


@login_required
def mis_tickets_detalle_view(request, ticket_id):
    """Vista para mostrar el detalle completo del ticket en móvil (Docente)"""
    # Si es PC, redirigir a la vista desktop con panel lateral
    if not is_mobile_device(request):
        estado = request.GET.get('estado', 'todos')
        orden = request.GET.get('orden', 'reciente')
        return redirect(f"{reverse('mis_tickets', args=[ticket_id])}?estado={estado}&orden={orden}")
    
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'Docente':
            return redirect('index')
    except Usuario.DoesNotExist:
        return redirect('index')

    ticket_seleccionado = get_object_or_404(Ticket, pk=ticket_id, usuario_creador=usuario)
    
    # Procesar POST (agregar comentario)
    if request.method == 'POST':
        comentario_texto = request.POST.get('comentario', '').strip()
        if comentario_texto:
            Comentario.objects.create(
                ticket=ticket_seleccionado,
                autor=usuario,
                texto=comentario_texto
            )
            estado_filtro = request.GET.get('estado', 'todos')
            orden = request.GET.get('orden', 'reciente')
            return redirect(f"{reverse('mis_tickets_detalle', args=[ticket_id])}?estado={estado_filtro}&orden={orden}")
    
    comentarios = Comentario.objects.filter(ticket=ticket_seleccionado).order_by('fecha_creacion')
    
    context = {
        'ticket_seleccionado': ticket_seleccionado,
        'comentarios': comentarios,
        'estado_actual': request.GET.get('estado', 'todos'),
        'orden_actual': request.GET.get('orden', 'reciente'),
    }
    
    return render(request, 'mis_tickets_detalle.html', context)


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
        if usuario.rol.nombre not in ['Admin', 'Superadmin']:
            return redirect('index') 
    except Usuario.DoesNotExist:
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
        if usuario.rol.nombre not in ['Admin', 'Superadmin']:
            return redirect('index')
    except Usuario.DoesNotExist:
        if not request.user.is_superuser:
             return redirect('index')
    # --- FIN DEL BLOQUE ---

    # --- PROCESAMIENTO DE FECHAS ---
    fecha_desde_str = request.GET.get('fecha_desde', '')
    fecha_hasta_str = request.GET.get('fecha_hasta', '')

    fecha_desde = None
    fecha_hasta = None

    try:
        if fecha_desde_str:
            fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d').date()
    except ValueError:
        fecha_desde = None

    try:
        if fecha_hasta_str:
            fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date()
    except ValueError:
        fecha_hasta = None

    # --- Query base con filtro de fecha aplicado ---
    base_query = Ticket.objects.all()

    if fecha_desde and fecha_hasta:
        base_query = base_query.filter(fecha_creacion__range=(fecha_desde, fecha_hasta))
    elif fecha_desde:
        base_query = base_query.filter(fecha_creacion__gte=fecha_desde)
    elif fecha_hasta:
         base_query = base_query.filter(fecha_creacion__lte=fecha_hasta)

    # --- REPORTES ---
    
    # 1. Reporte: Conteo de Tickets por Estado
    conteo_por_estado = base_query.values('estado').annotate(
        total=Count('ticket_id')
    ).order_by('estado')

    reporte_estados = [
        {
            'estado': dict(Ticket.ESTADO_CHOICES).get(item['estado'], item['estado']),
            'total': item['total']
        }
        for item in conteo_por_estado
    ]

    # 2. Reporte: Conteo de Tickets por Categoría
    conteo_por_categoria = base_query.values('categoria__nombre').annotate(
        total=Count('ticket_id')
    ).order_by('categoria__nombre')

    reporte_categorias = [
        {
            'categoria': item['categoria__nombre'] if item['categoria__nombre'] else 'Sin categoría',
            'total': item['total']
        }
        for item in conteo_por_categoria
    ]

    # 3. Reporte: Conteo de Tickets por Prioridad
    conteo_por_prioridad = base_query.values('prioridad__Tipo_Nivel').annotate(
        total=Count('ticket_id')
    ).order_by('prioridad__Tipo_Nivel')

    prioridad_map = dict(Prioridad.NIVEL_CHOICES)
    reporte_prioridades = [
        {
            'prioridad': prioridad_map.get(item['prioridad__Tipo_Nivel'], 'Desconocida'),
            'total': item['total']
        }
        for item in conteo_por_prioridad
    ]

    # --- COMPARACIÓN MES ACTUAL VS MES ANTERIOR ---
    ahora = timezone.now()
    mes_actual = ahora.month
    anio_actual = ahora.year
    
    # Calcular mes anterior
    if mes_actual == 1:
        mes_anterior = 12
        anio_anterior = anio_actual - 1
    else:
        mes_anterior = mes_actual - 1
        anio_anterior = anio_actual
    
    # Contar tickets del mes actual
    tickets_mes_actual = Ticket.objects.filter(
        fecha_creacion__year=anio_actual,
        fecha_creacion__month=mes_actual
    ).count()
    
    # Contar tickets del mes anterior
    tickets_mes_anterior = Ticket.objects.filter(
        fecha_creacion__year=anio_anterior,
        fecha_creacion__month=mes_anterior
    ).count()
    
    # Calcular porcentaje de cambio
    if tickets_mes_anterior > 0:
        porcentaje_cambio = ((tickets_mes_actual - tickets_mes_anterior) / tickets_mes_anterior) * 100
    else:
        porcentaje_cambio = 100 if tickets_mes_actual > 0 else 0
    
    # Nombres de meses en español
    meses_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    comparacion_mensual = {
        'mes_actual': meses_es[mes_actual],
        'tickets_mes_actual': tickets_mes_actual,
        'mes_anterior': meses_es[mes_anterior],
        'tickets_mes_anterior': tickets_mes_anterior,
        'porcentaje_cambio': round(porcentaje_cambio, 1),
        'aumento': porcentaje_cambio > 0
    }

    context = {
        'view_class': 'view-dashboard',
        'reporte_estados': reporte_estados,
        'reporte_categorias': reporte_categorias,
        'reporte_prioridades': reporte_prioridades,
        'fecha_desde_str': fecha_desde_str,
        'fecha_hasta_str': fecha_hasta_str,
        'comparacion_mensual': comparacion_mensual,
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
    # --- BLOQUE DE PERMISO (Admin y Superadmin) ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre not in ['Admin', 'Superadmin']:
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

# ==========================================
# VISTAS DE GESTIÓN DE USUARIOS (SUPERADMIN)
# ==========================================

@login_required
def usuarios_list_view(request):
    """
    Lista todos los usuarios del sistema (solo para Superadmin).
    """
    # --- BLOQUE DE PERMISO ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre not in ['Superadmin', 'Admin']:
            return redirect('index')
    except Usuario.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('index')
    # --- FIN DEL BLOQUE ---

    # Obtener parámetros de filtro
    rol_filtro = request.GET.get('rol', '')
    estado_filtro = request.GET.get('estado', '')  # 'activo' o 'inactivo'
    busqueda = request.GET.get('busqueda', '')

    # Query base
    usuarios_query = Usuario.objects.select_related('rol').all()

    # Filtrar por rol
    if rol_filtro:
        usuarios_query = usuarios_query.filter(rol__nombre=rol_filtro)

    # Filtrar por estado (activo/inactivo)
    if estado_filtro == 'activo':
        usuarios_query = usuarios_query.filter(activo=True)
    elif estado_filtro == 'inactivo':
        usuarios_query = usuarios_query.filter(activo=False)

    # Búsqueda por nombre o email
    if busqueda:
        usuarios_query = usuarios_query.filter(
            nombre__icontains=busqueda
        ) | usuarios_query.filter(
            email__icontains=busqueda
        )

    # Ordenar por fecha de creación (más recientes primero)
    usuarios_list = usuarios_query.order_by('-fecha_creacion')

    # Obtener lista de roles para el filtro
    roles_disponibles = Rol.objects.all()

    context = {
        'view_class': 'view-dashboard',
        'usuarios': usuarios_list,
        'roles_disponibles': roles_disponibles,
        'rol_filtro': rol_filtro,
        'estado_filtro': estado_filtro,
        'busqueda': busqueda,
    }
    return render(request, 'usuarios_list.html', context)


@login_required
def usuario_create_view(request):
    """
    Crear un nuevo usuario (solo para Superadmin).
    """
    # --- BLOQUE DE PERMISO ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre not in ['Superadmin', 'Admin']:
            return redirect('index')
    except Usuario.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('index')
    # --- FIN DEL BLOQUE ---

    if request.method == 'POST':
        form = UsuarioForm(request.POST, is_edit=False)
        if form.is_valid():
            form.save()
            return redirect('usuarios_list')
    else:
        form = UsuarioForm(is_edit=False)

    context = {
        'view_class': 'view-dashboard',
        'form': form,
        'titulo': 'Crear Nuevo Usuario',
        'boton_texto': 'Crear Usuario',
    }
    return render(request, 'usuario_form.html', context)


@login_required
def usuario_edit_view(request, rut):
    """
    Editar un usuario existente (solo para Superadmin).
    """
    # --- BLOQUE DE PERMISO ---
    try:
        usuario_actual = Usuario.objects.get(email=request.user.email)
        if usuario_actual.rol.nombre not in ['Superadmin', 'Admin']:
            return redirect('index')
    except Usuario.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('index')
    # --- FIN DEL BLOQUE ---

    usuario_editar = get_object_or_404(Usuario, pk=rut)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario_editar, is_edit=True)
        if form.is_valid():
            form.save()
            return redirect('usuarios_list')
    else:
        form = UsuarioForm(instance=usuario_editar, is_edit=True)

    context = {
        'view_class': 'view-dashboard',
        'form': form,
        'usuario_editar': usuario_editar,
        'titulo': f'Editar Usuario: {usuario_editar.nombre}',
        'boton_texto': 'Guardar Cambios',
    }
    return render(request, 'usuario_form.html', context)


@login_required
def usuario_toggle_estado_view(request, rut):
    """
    Activar/Desactivar un usuario (cambiar campo 'activo').
    """
    # --- BLOQUE DE PERMISO ---
    try:
        usuario_actual = Usuario.objects.get(email=request.user.email)
        if usuario_actual.rol.nombre not in ['Superadmin', 'Admin']:
            return redirect('index')
    except Usuario.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('index')
    # --- FIN DEL BLOQUE ---

    usuario = get_object_or_404(Usuario, pk=rut)
    
    # Cambiar estado
    usuario.activo = not usuario.activo
    usuario.save()

    return redirect('usuarios_list')


@login_required
def usuario_detail_view(request, rut):
    """
    Ver detalles de un usuario específico.
    """
    # --- BLOQUE DE PERMISO ---
    try:
        usuario_actual = Usuario.objects.get(email=request.user.email)
        if usuario_actual.rol.nombre not in ['Superadmin', 'Admin']:
            return redirect('index')
    except Usuario.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('index')
    # --- FIN DEL BLOQUE ---

    usuario = get_object_or_404(Usuario.objects.select_related('rol'), pk=rut)
    
    # Estadísticas del usuario
    tickets_creados = Ticket.objects.filter(usuario_creador=usuario).count()
    tickets_asignados = AsignacionTicket.objects.filter(usuario_asignado=usuario).count()
    comentarios_realizados = Comentario.objects.filter(autor=usuario).count()

    context = {
        'view_class': 'view-dashboard',
        'usuario_detalle': usuario,
        'tickets_creados': tickets_creados,
        'tickets_asignados': tickets_asignados,
        'comentarios_realizados': comentarios_realizados,
    }
    return render(request, 'usuario_detail.html', context)

@login_required
def descargar_reporte_csv(request):
    """
    Genera y descarga un archivo CSV con los reportes filtrados.
    """
    import csv
    from django.http import HttpResponse
    
    # --- BLOQUE DE PERMISO ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre not in ['Admin', 'Superadmin']:
            return redirect('index')
    except Usuario.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('index')
    # --- FIN DEL BLOQUE ---

    # Obtener los mismos filtros que en la vista de reportes
    fecha_desde_str = request.GET.get('fecha_desde', '')
    fecha_hasta_str = request.GET.get('fecha_hasta', '')

    fecha_desde = None
    fecha_hasta = None

    try:
        if fecha_desde_str:
            fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d').date()
    except ValueError:
        fecha_desde = None

    try:
        if fecha_hasta_str:
            fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date()
    except ValueError:
        fecha_hasta = None

    # Query base con filtros
    base_query = Ticket.objects.all()

    if fecha_desde and fecha_hasta:
        base_query = base_query.filter(fecha_creacion__range=(fecha_desde, fecha_hasta))
    elif fecha_desde:
        base_query = base_query.filter(fecha_creacion__gte=fecha_desde)
    elif fecha_hasta:
        base_query = base_query.filter(fecha_creacion__lte=fecha_hasta)

    # Crear respuesta HTTP con tipo CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="reporte_tickets_{timestamp}.csv"'

    # Escribir BOM para UTF-8 (ayuda a Excel a reconocer caracteres especiales)
    response.write('\ufeff')

    writer = csv.writer(response)

    # --- SECCIÓN 1: ENCABEZADO ---
    writer.writerow(['REPORTE DE TICKETS'])
    writer.writerow([])
    
    if fecha_desde_str or fecha_hasta_str:
        periodo = f"Desde: {fecha_desde_str or 'Inicio'} - Hasta: {fecha_hasta_str or 'Hoy'}"
        writer.writerow(['Período:', periodo])
    else:
        writer.writerow(['Período:', 'Todos los tickets'])
    
    writer.writerow([])
    
    # --- SECCIÓN 2: TICKETS POR ESTADO ---
    writer.writerow(['TICKETS POR ESTADO'])
    writer.writerow(['Estado', 'Cantidad'])

    conteo_por_estado = base_query.values('estado').annotate(total=Count('ticket_id')).order_by('estado')
    for item in conteo_por_estado:
        estado_display = dict(Ticket.ESTADO_CHOICES).get(item['estado'], item['estado'])
        writer.writerow([estado_display, item['total']])

    writer.writerow([])

    # --- SECCIÓN 3: TICKETS POR CATEGORÍA ---
    writer.writerow(['TICKETS POR CATEGORÍA'])
    writer.writerow(['Categoría', 'Cantidad'])

    conteo_por_categoria = base_query.values('categoria__nombre').annotate(total=Count('ticket_id')).order_by('categoria__nombre')
    for item in conteo_por_categoria:
        categoria = item['categoria__nombre'] if item['categoria__nombre'] else 'Sin categoría'
        writer.writerow([categoria, item['total']])

    writer.writerow([])

    # --- SECCIÓN 4: TICKETS POR PRIORIDAD ---
    writer.writerow(['TICKETS POR PRIORIDAD'])
    writer.writerow(['Prioridad', 'Cantidad'])

    conteo_por_prioridad = base_query.values('prioridad__Tipo_Nivel').annotate(total=Count('ticket_id')).order_by('prioridad__Tipo_Nivel')
    prioridad_map = dict(Prioridad.NIVEL_CHOICES)
    
    for item in conteo_por_prioridad:
        prioridad = prioridad_map.get(item['prioridad__Tipo_Nivel'], 'Desconocida')
        writer.writerow([prioridad, item['total']])

    writer.writerow([])

    # --- SECCIÓN 5: COMPARACIÓN MENSUAL ---
    ahora = timezone.now()
    mes_actual = ahora.month
    anio_actual = ahora.year
    
    if mes_actual == 1:
        mes_anterior = 12
        anio_anterior = anio_actual - 1
    else:
        mes_anterior = mes_actual - 1
        anio_anterior = anio_actual
    
    tickets_mes_actual = Ticket.objects.filter(
        fecha_creacion__year=anio_actual,
        fecha_creacion__month=mes_actual
    ).count()
    
    tickets_mes_anterior = Ticket.objects.filter(
        fecha_creacion__year=anio_anterior,
        fecha_creacion__month=mes_anterior
    ).count()
    
    if tickets_mes_anterior > 0:
        porcentaje_cambio = ((tickets_mes_actual - tickets_mes_anterior) / tickets_mes_anterior) * 100
    else:
        porcentaje_cambio = 100 if tickets_mes_actual > 0 else 0
    
    meses_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    writer.writerow(['COMPARACIÓN MENSUAL'])
    writer.writerow(['Mes', 'Cantidad'])
    writer.writerow([f'{meses_es[mes_anterior]} {anio_anterior}', tickets_mes_anterior])
    writer.writerow([f'{meses_es[mes_actual]} {anio_actual}', tickets_mes_actual])
    writer.writerow(['Variación', f'{porcentaje_cambio:+.1f}%'])

    return response

@require_POST
@login_required
def toggle_fijar_ticket_view(request, ticket_id):
    """
    Alterna el estado de fijado de un ticket (solo para TI).
    """
    # --- BLOQUE DE PERMISO ---
    try:
        usuario = Usuario.objects.get(email=request.user.email)
        if usuario.rol.nombre != 'TI':
            return redirect('index')
    except Usuario.DoesNotExist:
        return redirect('index')
    # --- FIN DEL BLOQUE ---

    # Busca el ticket asignado al técnico actual
    asignacion = AsignacionTicket.objects.filter(
        ticket_id=ticket_id,
        usuario_asignado=usuario
    ).first()
    
    if not asignacion:
        return redirect('mis_asignaciones')
    
    ticket = asignacion.ticket
    
    # Si el ticket está resuelto o cerrado, no se puede fijar
    if ticket.estado in ['RESUELTO', 'CERRADO']:
        ticket.fijado = False
    else:
        # Alterna el estado de fijado
        ticket.fijado = not ticket.fijado
    
    ticket.save()
    
    # Redirige manteniendo los filtros
    estado_filtro = request.GET.get('estado', '')
    orden = request.GET.get('orden', 'reciente')
    return redirect(f"{reverse('mis_asignaciones')}?estado={estado_filtro}&orden={orden}")


@login_required
def cambiar_contrasenia_view(request):
    """
    Vista para cambiar la contraseña del usuario autenticado
    """
    try:
        usuario_app = Usuario.objects.get(email=request.user.email)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('index')
    
    if request.method == 'POST':
        form = CambiarContraseniaForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # Mantener la sesión activa después de cambiar la contraseña
            update_session_auth_hash(request, request.user)
            messages.success(request, '¡Contraseña actualizada exitosamente!')
            return redirect('index')
    else:
        form = CambiarContraseniaForm(request.user)
    
    context = {
        'usuario': usuario_app,
        'form': form,
        'view_class': 'view-cambiar-contrasenia'
    }
    return render(request, 'cambiar_contrasenia.html', context)


@login_required
def cambiar_contrasenia_ajax(request):
    """
    Vista AJAX para cambiar la contraseña del usuario desde el modal
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        contrasenia_actual = data.get('contrasenia_actual', '').strip()
        nueva_contrasenia = data.get('nueva_contrasenia', '').strip()
        confirmar_contrasenia = data.get('confirmar_contrasenia', '').strip()
        
        # Validaciones
        if not all([contrasenia_actual, nueva_contrasenia, confirmar_contrasenia]):
            return JsonResponse({'success': False, 'error': 'Todos los campos son requeridos'})
        
        # Verificar contraseña actual
        if not request.user.check_password(contrasenia_actual):
            return JsonResponse({'success': False, 'error': 'La contraseña actual es incorrecta'})
        
        # Verificar que las nuevas contraseñas coincidan
        if nueva_contrasenia != confirmar_contrasenia:
            return JsonResponse({'success': False, 'error': 'Las contraseñas nuevas no coinciden'})
        
        # Verificar longitud mínima
        if len(nueva_contrasenia) < 6:
            return JsonResponse({'success': False, 'error': 'La contraseña debe tener al menos 6 caracteres'})
        
        # Cambiar la contraseña en Django User
        request.user.set_password(nueva_contrasenia)
        request.user.save()
        
        # Mantener la sesión activa después de cambiar la contraseña
        update_session_auth_hash(request, request.user)
        
        return JsonResponse({'success': True, 'message': 'Contraseña actualizada exitosamente'})
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error inesperado: {str(e)}'})