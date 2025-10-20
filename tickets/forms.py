# tickets/forms.py
from django import forms
from .models import Ticket, AsignacionTicket, Usuario, Rol, Comentario, Prioridad, Categoria

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        # Estos son los campos que aparecerán en el formulario
        fields = ['titulo', 'descripcion']
        
        # Opcional: Esto hace que los campos se vean un poco mejor
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }

class AsignacionTicketForm(forms.ModelForm):
    
    # 1. Definimos el campo, pero con un queryset vacío.
    #    No consultamos la BD aquí.
    usuario_asignado = forms.ModelChoiceField(
        queryset=Usuario.objects.none(), # Empezamos con un queryset vacío
        label="Asignar a Técnico",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    prioridad = forms.ModelChoiceField(
        queryset=Prioridad.objects.all(),
        label="Prioridad del Ticket",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        label="Categoría del Ticket",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = AsignacionTicket
        fields = ['usuario_asignado', 'comentarios', 'prioridad', 'categoria'] 
        widgets = {
            'comentarios': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Añade un comentario (opcional)...'}),
        }

    # 2. Usamos __init__ para llenar el queryset dinámicamente
    #    Este código SÍ se ejecuta cada vez que el formulario se usa,
    #    no cuando el servidor arranca.
    def __init__(self, *args, **kwargs):

        ticket_instance = kwargs.pop('ticket', None) 
        super().__init__(*args, **kwargs) # Llamamos al __init__ original SIN 'ticket'

        # Re-aplicamos el filtro de rol TI aquí después de llamar a super()
        try:
            rol_tecnico = Rol.objects.get(nombre='TI')
            self.fields['usuario_asignado'].queryset = Usuario.objects.filter(rol=rol_tecnico)
        except Rol.DoesNotExist:
            self.fields['usuario_asignado'].queryset = Usuario.objects.none()

        # Si recibimos un ticket (lo sacamos antes con pop), pre-seleccionamos
        if ticket_instance:
            self.fields['prioridad'].initial = ticket_instance.prioridad
            self.fields['categoria'].initial = ticket_instance.categoria

        super().__init__(*args, **kwargs) # Llamamos al __init__ original
        
        try:
            # Buscamos el rol. ¡Asegúrate de que el nombre 'Técnico' exista en tu BD!
            rol_tecnico = Rol.objects.get(nombre='TI')
            # Asignamos el queryset filtrado al campo
            self.fields['usuario_asignado'].queryset = Usuario.objects.filter(rol=rol_tecnico)
        except Rol.DoesNotExist:
            # Si el rol no existe, el queryset simplemente quedará vacío
            # (Usuario.objects.none()), pero la app no se romperá.
            self.fields['usuario_asignado'].queryset = Usuario.objects.none()
        
        ticket_instance = kwargs.pop('ticket', None) 
        super().__init__(*args, **kwargs)

        # Re-aplicamos el filtro de rol TI aquí después de llamar a super()
        try:
            rol_tecnico = Rol.objects.get(nombre='TI')
            self.fields['usuario_asignado'].queryset = Usuario.objects.filter(rol=rol_tecnico)
        except Rol.DoesNotExist:
            self.fields['usuario_asignado'].queryset = Usuario.objects.none()

        # Si recibimos un ticket, pre-seleccionamos su prioridad y categoría
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