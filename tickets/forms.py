# tickets/forms.py
from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        # Estos son los campos que aparecerán en el formulario
        fields = ['titulo', 'descripcion', 'prioridad', 'categoria']
        
        # Opcional: Esto hace que los campos se vean un poco mejor
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
        }