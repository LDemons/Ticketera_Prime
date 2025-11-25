from django import forms
from .models import Ticket, AsignacionTicket, Usuario, Rol, Comentario, Prioridad, Categoria
from django.contrib.auth.hashers import make_password

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

class UsuarioForm(forms.ModelForm):
    """
    Formulario para crear/editar usuarios desde el panel de Superadmin.
    """
    # Campo para la contraseña (no se guarda directamente en el modelo)
    contrasenia = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        required=False,  # Opcional en edición
        label='Contraseña',
        help_text='Deja en blanco para mantener la contraseña actual (solo en edición)'
    )
    
    confirmar_contrasenia = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        required=False,
        label='Confirmar Contraseña'
    )

    class Meta:
        model = Usuario
        fields = ['rut', 'dv', 'nombre', 'email', 'rol', 'activo']
        widgets = {
            'rut': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '12345678'}),
            'dv': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Juan Pérez'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'usuario@colegio.cl'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        labels = {
            'rut': 'RUT (sin puntos ni guión)',
            'dv': 'Dígito Verificador',
            'nombre': 'Nombre Completo',
            'email': 'Correo Electrónico',
            'rol': 'Rol del Usuario',
            'activo': 'Usuario Activo',
        }

    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)  # Flag para saber si es edición
        super().__init__(*args, **kwargs)
        
        # En modo edición, el RUT no se puede cambiar (es la PK)
        if self.is_edit:
            self.fields['rut'].disabled = True
            self.fields['contrasenia'].required = False
            self.fields['confirmar_contrasenia'].required = False
        else:
            # En creación, la contraseña es obligatoria
            self.fields['contrasenia'].required = True
            self.fields['confirmar_contrasenia'].required = True

    def clean(self):
        cleaned_data = super().clean()
        contrasenia = cleaned_data.get('contrasenia')
        confirmar = cleaned_data.get('confirmar_contrasenia')

        # Validar contraseñas solo si se ingresaron
        if contrasenia or confirmar:
            if contrasenia != confirmar:
                raise forms.ValidationError('Las contraseñas no coinciden.')
            
            if len(contrasenia) < 6:
                raise forms.ValidationError('La contraseña debe tener al menos 6 caracteres.')

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        
        # Si se ingresó una nueva contraseña, hashearla
        contrasenia = self.cleaned_data.get('contrasenia')
        if contrasenia:
            usuario.contrasenia_hash = make_password(contrasenia)
        
        if commit:
            usuario.save()
        return usuario