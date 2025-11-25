from django import forms
from .models import Ticket, AsignacionTicket, Usuario, Rol, Comentario, Prioridad, Categoria

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        # Estos son los campos que aparecerán en el formulario
        fields = ['titulo', 'descripcion']
        
        # Esto hace que los campos se vean un poco mejor
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }

class AsignacionTicketForm(forms.ModelForm):
    """
    Formulario para asignar un ticket a un técnico.
    Incluye campos adicionales para editar prioridad y categoría del ticket.
    """
    
    # Campos adicionales (no pertenecen a AsignacionTicket)
    prioridad = forms.ModelChoiceField(
        queryset=Prioridad.objects.all(), 
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(), 
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = AsignacionTicket
        fields = ['usuario_asignado', 'comentarios', 'prioridad', 'categoria'] 
        widgets = {
            'comentarios': forms.Textarea(attrs={
                'class': 'form-input', 
                'rows': 3, 
                'placeholder': 'Añade un comentario (opcional)...'
            }),
        }

    def __init__(self, *args, **kwargs):
        ticket_instance = kwargs.pop('ticket', None) 
        super().__init__(*args, **kwargs)

        # IMPORTANTE: Hacer el campo comentarios opcional
        self.fields['comentarios'].required = False

        # Filtrar solo usuarios con rol TI
        try:
            rol_tecnico = Rol.objects.get(nombre='TI')
            self.fields['usuario_asignado'].queryset = Usuario.objects.filter(rol=rol_tecnico)
        except Rol.DoesNotExist:
            self.fields['usuario_asignado'].queryset = Usuario.objects.none()

        # Si recibimos un ticket, pre-seleccionamos prioridad y categoría
        if ticket_instance:
            self.fields['prioridad'].initial = ticket_instance.prioridad
            self.fields['categoria'].initial = ticket_instance.categoria

class GestionTicketForm(forms.ModelForm):
    """
    Un formulario para que el técnico gestione un ticket.
    """
    
    # Traemos los ESTADO_CHOICES del modelo Ticket
    # Excluimos 'ABIERTO' porque un ticket gestionado ya no puede volver a "Abierto"
    ESTADOS_TECNICO = [choice for choice in Ticket.ESTADO_CHOICES if choice[0] != 'ABIERTO']

    # 1. Creamos un campo para actualizar el estado del Ticket
    estado = forms.ChoiceField(
        choices=ESTADOS_TECNICO,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # 2. Usamos el ModelForm para el campo 'contenido' del Comentario
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Añade una respuesta o nota interna...'}),
        }
        labels = {
            'contenido': 'Añadir Comentario/Respuesta',
        }

class ComentarioForm(forms.ModelForm):
    """
    Formulario simple para que un usuario añada un comentario.
    """
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Escribe una respuesta o seguimiento...'}),
        }
        labels = {
            'contenido': 'Añadir Comentario:'
        }