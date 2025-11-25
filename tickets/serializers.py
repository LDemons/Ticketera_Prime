"""
Serializers para la API REST de Ticketera Prime
Convierte los modelos de Django a JSON y viceversa
"""

from rest_framework import serializers
from .models import Ticket, Usuario, Comentario, Categoria, Prioridad, Notificacion, AsignacionTicket


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializador básico para Usuario"""
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['rut', 'dv', 'nombre', 'email', 'rol_nombre', 'activo']
        read_only_fields = ['rut', 'dv']


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializador para Categorías"""
    class Meta:
        model = Categoria
        fields = ['categoria_id', 'nombre', 'descripcion']


class PrioridadSerializer(serializers.ModelSerializer):
    """Serializador para Prioridades"""
    class Meta:
        model = Prioridad
        fields = ['prioridad_id', 'Tipo_Nivel', 'sla_horas']


class ComentarioSerializer(serializers.ModelSerializer):
    """Serializador para Comentarios"""
    autor_nombre = serializers.CharField(source='autor.nombre', read_only=True)
    autor_rol = serializers.CharField(source='autor.rol.nombre', read_only=True)
    
    class Meta:
        model = Comentario
        fields = ['comentario_id', 'contenido', 'autor_nombre', 'autor_rol', 'fecha_creacion']
        read_only_fields = ['comentario_id', 'fecha_creacion']


class TicketListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listado de tickets"""
    usuario_creador_nombre = serializers.CharField(source='usuario_creador.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    prioridad_nivel = serializers.CharField(source='prioridad.Tipo_Nivel', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'ticket_id', 'titulo', 'estado', 'estado_display',
            'usuario_creador_nombre', 'categoria_nombre', 
            'prioridad_nivel', 'fecha_creacion', 'fijado'
        ]


class TicketDetailSerializer(serializers.ModelSerializer):
    """Serializador completo para detalle de ticket"""
    usuario_creador = UsuarioSerializer(read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    prioridad = PrioridadSerializer(read_only=True)
    comentarios = ComentarioSerializer(many=True, read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'ticket_id', 'titulo', 'descripcion', 'estado', 'estado_display',
            'usuario_creador', 'categoria', 'prioridad', 
            'fecha_creacion', 'fijado', 'comentarios'
        ]
        read_only_fields = ['ticket_id', 'fecha_creacion']


class TicketCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear tickets (solo para Docentes)"""
    
    class Meta:
        model = Ticket
        fields = ['titulo', 'descripcion']
    
    def validate_titulo(self, value):
        """Validar que el título no esté vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("El título no puede estar vacío.")
        return value.strip()
    
    def validate_descripcion(self, value):
        """Validar que la descripción no esté vacía"""
        if not value or not value.strip():
            raise serializers.ValidationError("La descripción no puede estar vacía.")
        return value.strip()
    
    def create(self, validated_data):
        """Crear ticket con estado inicial ABIERTO y valores por defecto para categoría y prioridad"""
        validated_data['estado'] = 'ABIERTO'
        
        # Asignar categoría por defecto si no existe
        if 'categoria' not in validated_data:
            try:
                categoria_pendiente = Categoria.objects.get(nombre='Pendiente de clasificación')
            except Categoria.DoesNotExist:
                # Si no existe, usar la primera categoría disponible
                categoria_pendiente = Categoria.objects.first()
            validated_data['categoria'] = categoria_pendiente
        
        # Asignar prioridad por defecto si no existe
        if 'prioridad' not in validated_data:
            try:
                prioridad_media = Prioridad.objects.get(Tipo_Nivel='MEDIO')
            except Prioridad.DoesNotExist:
                # Si no existe, usar la primera prioridad disponible
                prioridad_media = Prioridad.objects.first()
            validated_data['prioridad'] = prioridad_media
        
        return super().create(validated_data)


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializador para Notificaciones"""
    ticket_titulo = serializers.CharField(source='ticket.titulo', read_only=True)
    ticket_id = serializers.IntegerField(source='ticket.ticket_id', read_only=True)
    
    class Meta:
        model = Notificacion
        fields = ['notificacion_id', 'mensaje', 'leido', 'fecha_creacion', 'ticket_id', 'ticket_titulo']
        read_only_fields = ['notificacion_id', 'fecha_creacion']


class ComentarioCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear comentarios"""
    
    class Meta:
        model = Comentario
        fields = ['contenido']
    
    def validate_contenido(self, value):
        """Validar que el comentario no esté vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("El comentario no puede estar vacío.")
        return value.strip()
