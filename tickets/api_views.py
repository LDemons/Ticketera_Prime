"""
Vistas API REST para la aplicación móvil de Ticketera Prime
Proporciona endpoints para autenticación, tickets, notificaciones y más
"""

from rest_framework import viewsets, status, generics, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Ticket, Usuario, Comentario, Notificacion, Categoria, Prioridad
from .serializers import (
    TicketListSerializer, TicketDetailSerializer, TicketCreateSerializer,
    ComentarioSerializer, ComentarioCreateSerializer, NotificacionSerializer,
    CategoriaSerializer, PrioridadSerializer, UsuarioSerializer
)


# ==========================================
# AUTENTICACIÓN
# ==========================================

@method_decorator(csrf_exempt, name='dispatch')
class CustomAuthToken(ObtainAuthToken):
    """
    Vista personalizada para autenticación con username y contraseña.
    Usa el sistema de autenticación estándar de Django.
    
    POST /api/v1/auth/login/
    Body: {"email": "PauloG", "password": "password123"}
    Response: {"token": "...", "user": {...}}
    """
    def post(self, request, *args, **kwargs):
        username = request.data.get('email')  # Mantener nombre del campo por compatibilidad
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Usuario y contraseña son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Autenticar con el sistema de Django
            from django.contrib.auth import authenticate
            from django.contrib.auth.models import User
            
            django_user = authenticate(username=username, password=password)
            
            if not django_user:
                return Response(
                    {'error': 'Credenciales inválidas'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Buscar usuario en el modelo de la app por email
            try:
                usuario_app = Usuario.objects.select_related('rol').get(email=django_user.email)
            except Usuario.DoesNotExist:
                return Response(
                    {'error': 'Usuario no encontrado en el sistema'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que esté activo
            if not usuario_app.activo:
                return Response(
                    {'error': 'Usuario inactivo'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Obtener o crear token
            token, created = Token.objects.get_or_create(user=django_user)
            
            return Response({
                'token': token.key,
                'user': {
                    'rut': usuario_app.rut,
                    'nombre': usuario_app.nombre,
                    'email': usuario_app.email,
                    'rol': usuario_app.rol.nombre,
                }
            })
            
        except Exception as e:
            return Response(
                {'error': 'Error en la autenticación'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==========================================
# VIEWSETS PRINCIPALES
# ==========================================

class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Tickets.
    
    Permisos por rol:
    - Docentes: Solo ven y crean sus propios tickets
    - TI: Ven tickets asignados a ellos
    - Admin/Superadmin: Ven todos los tickets
    
    Endpoints:
    - GET /api/v1/tickets/ - Listar tickets
    - POST /api/v1/tickets/ - Crear ticket (solo Docente)
    - GET /api/v1/tickets/{id}/ - Detalle de ticket
    - POST /api/v1/tickets/{id}/add_comment/ - Añadir comentario
    - POST /api/v1/tickets/{id}/toggle_pin/ - Fijar/desfijar (solo TI)
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar tickets según el rol del usuario"""
        user = self.request.user
        try:
            usuario_app = Usuario.objects.get(email=user.email)
            
            if usuario_app.rol.nombre == 'Docente':
                # Docente solo ve sus tickets
                return Ticket.objects.filter(
                    usuario_creador=usuario_app
                ).select_related('usuario_creador', 'categoria', 'prioridad').order_by('-fecha_creacion')
            
            elif usuario_app.rol.nombre == 'TI':
                # TI ve tickets asignados a él
                from .models import AsignacionTicket
                tickets_asignados = AsignacionTicket.objects.filter(
                    usuario_asignado=usuario_app
                ).values_list('ticket_id', flat=True)
                return Ticket.objects.filter(
                    ticket_id__in=tickets_asignados
                ).select_related('usuario_creador', 'categoria', 'prioridad').order_by('-fijado', '-fecha_creacion')
            
            else:  # Admin o Superadmin
                return Ticket.objects.all().select_related(
                    'usuario_creador', 'categoria', 'prioridad'
                ).order_by('-fecha_creacion')
        
        except Usuario.DoesNotExist:
            return Ticket.objects.none()
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action == 'list':
            return TicketListSerializer
        elif self.action == 'create':
            return TicketCreateSerializer
        return TicketDetailSerializer
    
    def perform_create(self, serializer):
        """Crear ticket asignando el usuario creador"""
        user = self.request.user
        try:
            usuario_app = Usuario.objects.get(email=user.email)
            
            # Solo Docentes pueden crear tickets desde la app móvil
            if usuario_app.rol.nombre != 'Docente':
                raise serializers.ValidationError('Solo los docentes pueden crear tickets')
            
            serializer.save(usuario_creador=usuario_app)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError('Usuario no encontrado')
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """
        Añadir un comentario a un ticket
        
        POST /api/v1/tickets/{id}/add_comment/
        Body: {"contenido": "Comentario aquí"}
        """
        ticket = self.get_object()
        serializer = ComentarioCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                usuario_app = Usuario.objects.get(email=request.user.email)
                
                comentario = Comentario.objects.create(
                    ticket=ticket,
                    autor=usuario_app,
                    contenido=serializer.validated_data['contenido']
                )
                
                return Response(
                    ComentarioSerializer(comentario).data,
                    status=status.HTTP_201_CREATED
                )
            except Usuario.DoesNotExist:
                return Response(
                    {'error': 'Usuario no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def toggle_pin(self, request, pk=None):
        """
        Fijar/desfijar ticket (solo para TI)
        
        POST /api/v1/tickets/{id}/toggle_pin/
        Response: {"ticket_id": 123, "fijado": true}
        """
        ticket = self.get_object()
        
        try:
            usuario_app = Usuario.objects.get(email=request.user.email)
            
            if usuario_app.rol.nombre != 'TI':
                return Response(
                    {'error': 'Solo técnicos TI pueden fijar tickets'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            ticket.fijado = not ticket.fijado
            ticket.save()
            
            return Response({
                'ticket_id': ticket.ticket_id,
                'fijado': ticket.fijado
            })
        
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para Notificaciones.
    Solo lectura, se crean automáticamente por signals.
    
    Endpoints:
    - GET /api/v1/notificaciones/ - Listar notificaciones
    - GET /api/v1/notificaciones/{id}/ - Detalle de notificación
    - POST /api/v1/notificaciones/{id}/mark_read/ - Marcar como leída
    - POST /api/v1/notificaciones/mark_all_read/ - Marcar todas como leídas
    """
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Obtener notificaciones del usuario autenticado"""
        user = self.request.user
        try:
            usuario_app = Usuario.objects.get(email=user.email)
            return Notificacion.objects.filter(
                usuario_destino=usuario_app
            ).select_related('ticket').order_by('-fecha_creacion')
        except Usuario.DoesNotExist:
            return Notificacion.objects.none()
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Marcar una notificación como leída
        
        POST /api/v1/notificaciones/{id}/mark_read/
        """
        notificacion = self.get_object()
        notificacion.leido = True
        notificacion.save()
        return Response({'status': 'notificación marcada como leída'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Marcar todas las notificaciones como leídas
        
        POST /api/v1/notificaciones/mark_all_read/
        """
        user = request.user
        try:
            usuario_app = Usuario.objects.get(email=user.email)
            count = Notificacion.objects.filter(
                usuario_destino=usuario_app,
                leido=False
            ).update(leido=True)
            return Response({'status': f'{count} notificaciones marcadas como leídas'})
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


# ==========================================
# VISTAS AUXILIARES
# ==========================================

class CategoriaListView(generics.ListAPIView):
    """
    Lista de categorías disponibles para crear tickets
    
    GET /api/v1/categorias/
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = []  # Sin autenticación para facilitar uso en app móvil


class PrioridadListView(generics.ListAPIView):
    """
    Lista de prioridades disponibles para crear tickets
    
    GET /api/v1/prioridades/
    """
    queryset = Prioridad.objects.all()
    serializer_class = PrioridadSerializer
    permission_classes = []  # Sin autenticación para facilitar uso en app móvil


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Obtener perfil del usuario autenticado
    
    GET /api/v1/auth/profile/
    Response: {"rut": 12345678, "nombre": "...", "email": "...", ...}
    """
    try:
        usuario_app = Usuario.objects.select_related('rol').get(email=request.user.email)
        serializer = UsuarioSerializer(usuario_app)
        return Response(serializer.data)
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Estadísticas para el dashboard de la app móvil
    Solo disponible para Docentes
    
    GET /api/v1/stats/
    Response: {
        "total_tickets": 10,
        "abiertos": 3,
        "en_progreso": 2,
        "resueltos": 4,
        "cerrados": 1
    }
    """
    try:
        usuario_app = Usuario.objects.get(email=request.user.email)
        
        if usuario_app.rol.nombre == 'Docente':
            tickets = Ticket.objects.filter(usuario_creador=usuario_app)
            stats = {
                'total_tickets': tickets.count(),
                'abiertos': tickets.filter(estado='ABIERTO').count(),
                'en_progreso': tickets.filter(estado='EN_PROGRESO').count(),
                'resueltos': tickets.filter(estado='RESUELTO').count(),
                'cerrados': tickets.filter(estado='CERRADO').count(),
            }
        elif usuario_app.rol.nombre == 'TI':
            # Para TI, mostrar estadísticas de sus tickets asignados
            from .models import AsignacionTicket
            tickets_asignados = AsignacionTicket.objects.filter(
                usuario_asignado=usuario_app
            ).values_list('ticket_id', flat=True)
            tickets = Ticket.objects.filter(ticket_id__in=tickets_asignados)
            
            stats = {
                'total_tickets': tickets.count(),
                'abiertos': tickets.filter(estado='ABIERTO').count(),
                'en_progreso': tickets.filter(estado='EN_PROGRESO').count(),
                'resueltos': tickets.filter(estado='RESUELTO').count(),
                'cerrados': tickets.filter(estado='CERRADO').count(),
                'fijados': tickets.filter(fijado=True).count(),
            }
        else:
            stats = {
                'error': 'Estadísticas solo disponibles para Docentes y Técnicos TI'
            }
        
        return Response(stats)
    
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
