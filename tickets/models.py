from django.db import models

# --- Modelos sin dependencias ---

class Rol(models.Model):
    rol_id = models.SmallIntegerField(primary_key=True)
    nombre = models.CharField(max_length=120, unique=True)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    categoria_id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=120)

    def __str__(self):
        return self.nombre

class Prioridad(models.Model):
    NIVEL_CHOICES = [
        ('MEDIO', 'Medio'),
        ('ALTO', 'Alto'),
        ('BAJO', 'Bajo'),
    ]
    # Renombrado de Prioridades a Prioridad (singular) por convención de Django
    prioridad_id = models.BigAutoField(primary_key=True)
    Tipo_Nivel = models.CharField(max_length=12, choices=NIVEL_CHOICES, default='MEDIO')
    sla_horas = models.IntegerField() # En el DDL era NOT NULL, si puede ser nulo, agrega null=True, blank=True

    def __str__(self):
        return self.Tipo_Nivel

# --- Modelos con dependencias ---

class Usuario(models.Model):
    # Nota: Django tiene un sistema de usuarios robusto. Para proyectos reales,
    # se recomienda extender el modelo de usuario de Django en lugar de crear uno desde cero.
    # Este modelo se crea para ser fiel al DDL proporcionado.
    DV_CHOICES = [(str(i), str(i)) for i in range(10)] + [('K', 'K')]

    rut = models.IntegerField(primary_key=True)
    dv = models.CharField(max_length=1, choices=DV_CHOICES)
    nombre = models.CharField(max_length=120)
    email = models.EmailField(max_length=255, unique=True)
    contrasenia_hash = models.CharField(max_length=255) # Django gestiona el hash de contraseñas de forma segura
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT) # ON DELETE NO ACTION se traduce como PROTECT

    def __str__(self):
        return f"{self.nombre} ({self.rut}-{self.dv})"

class Ticket(models.Model):
    ESTADO_CHOICES = [
        ('ABIERTO', 'Abierto'),
        ('EN_PROGRESO', 'En Progreso'),
        ('RESUELTO', 'Resuelto'),
        ('CERRADO', 'Cerrado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    ticket_id = models.BigAutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=200) # Considera usar models.TextField() si la descripción puede ser más larga
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ABIERTO')
    # De DateField a DateTimeField
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    cerrado_en = models.DateField(null=True, blank=True)
    
    # Relaciones (Foreign Keys)
    usuario_creador = models.ForeignKey(
        Usuario, 
        on_delete=models.PROTECT, 
        related_name='tickets_creados'
    )
    prioridad = models.ForeignKey(Prioridad, on_delete=models.PROTECT)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)

    def __str__(self):
        return f"Ticket #{self.ticket_id}: {self.titulo}"

class AsignacionTicket(models.Model):
    asignacion_id = models.BigAutoField(primary_key=True)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    comentarios = models.CharField(max_length=255)

    # Relaciones (Foreign Keys)
    usuario_asignado = models.ForeignKey(
        Usuario, 
        on_delete=models.PROTECT,
        related_name='asignaciones'
    )
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE) # El DDL especifica ON DELETE CASCADE

    def __str__(self):
        return f"Asignación de {self.ticket} a {self.usuario_asignado}"
    
class Comentario(models.Model):
    comentario_id = models.BigAutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Comentario de {self.autor.nombre} en Ticket #{self.ticket.ticket_id}"

class Notificacion(models.Model):
    notificacion_id = models.BigAutoField(primary_key=True)
    
    # El usuario que RECIBE la notificación
    usuario_destino = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='notificaciones'
    )
    
    # El ticket al que se refiere la notificación
    ticket = models.ForeignKey(
        Ticket, 
        on_delete=models.CASCADE, 
        related_name='notificaciones_ticket'
    )
    
    mensaje = models.CharField(max_length=255)
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True) # Usamos DateTimeField

    def __str__(self):
        return f"Notificación para {self.usuario_destino.nombre}: {self.mensaje}"

    class Meta:
        # Ordenar las notificaciones más nuevas primero
        ordering = ['-fecha_creacion']