from django.contrib import admin
from .models import Rol, Categoria, Prioridad, Usuario, Ticket, AsignacionTicket

# Register your models here.

admin.site.register(Rol)
admin.site.register(Categoria)
admin.site.register(Prioridad)
admin.site.register(Usuario)
admin.site.register(Ticket)
admin.site.register(AsignacionTicket)