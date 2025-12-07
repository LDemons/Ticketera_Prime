from django import forms
from .models import Ticket, AsignacionTicket, Usuario, Rol, Comentario, Prioridad, Categoria
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

class TicketForm(forms.ModelForm):
    """
    Formulario simplificado para docentes - solo título y descripción.
    El admin asigna categoría y prioridad al momento de asignar el ticket.
    """
    class Meta:
        model = Ticket
        # Solo título y descripción para docentes
        fields = ['titulo', 'descripcion']
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Problema con proyector sala 201'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Describe el problema con el mayor detalle posible...'
            }),
        }
        labels = {
            'titulo': 'Título del Ticket',
            'descripcion': 'Descripción',
        }
    
    def save(self, commit=True):
        """
        Al guardar, asignar categoría y prioridad por defecto.
        """
        ticket = super().save(commit=False)
        
        # Asignar categoría por defecto si no existe
        if not ticket.categoria_id:
            try:
                categoria_pendiente = Categoria.objects.get(nombre='Pendiente de clasificación')
            except Categoria.DoesNotExist:
                categoria_pendiente = Categoria.objects.first()
            ticket.categoria = categoria_pendiente
        
        # Asignar prioridad por defecto si no existe
        if not ticket.prioridad_id:
            try:
                prioridad_media = Prioridad.objects.get(Tipo_Nivel='MEDIO')
            except Prioridad.DoesNotExist:
                prioridad_media = Prioridad.objects.first()
            ticket.prioridad = prioridad_media
        
        if commit:
            ticket.save()
        return ticket

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
        
        # Contraseña por defecto si no se especifica
        contrasenia = self.cleaned_data.get('contrasenia') or 'ticketera2025'
        
        # Actualizar el hash en el modelo Usuario
        # El signal crear_usuario_django se encargará de crear el Django User automáticamente
        usuario.contrasenia_hash = make_password(contrasenia)
        
        if commit:
            usuario.save()
            # Si es edición y cambió la contraseña, actualizar Django User
            if not self._state.adding and self.cleaned_data.get('contrasenia'):
                try:
                    django_user = User.objects.get(email__iexact=usuario.email)
                    django_user.set_password(contrasenia)
                    django_user.save()
                except User.DoesNotExist:
                    pass  # El signal lo creará
        
        return usuario


class CambiarContraseniaForm(forms.Form):
    """
    Formulario para que los usuarios cambien su contraseña desde el panel web
    """
    contrasenia_actual = forms.CharField(
        label='Contraseña Actual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ingresa tu contraseña actual'
        })
    )
    nueva_contrasenia = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Mínimo 6 caracteres'
        })
    )
    confirmar_contrasenia = forms.CharField(
        label='Confirmar Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Repite la nueva contraseña'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_contrasenia_actual(self):
        contrasenia_actual = self.cleaned_data.get('contrasenia_actual')
        if not self.user.check_password(contrasenia_actual):
            raise forms.ValidationError('La contraseña actual es incorrecta.')
        return contrasenia_actual

    def clean(self):
        cleaned_data = super().clean()
        nueva = cleaned_data.get('nueva_contrasenia')
        confirmar = cleaned_data.get('confirmar_contrasenia')

        if nueva and confirmar:
            if nueva != confirmar:
                raise forms.ValidationError('Las contraseñas nuevas no coinciden.')
            
            if len(nueva) < 6:
                raise forms.ValidationError('La contraseña debe tener al menos 6 caracteres.')

        return cleaned_data

    def save(self):
        """Guarda la nueva contraseña para el usuario"""
        nueva_contrasenia = self.cleaned_data['nueva_contrasenia']
        self.user.set_password(nueva_contrasenia)
        self.user.save()
        return self.user