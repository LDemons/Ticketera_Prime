"""
URL configuration for ticketera_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include 
from tickets import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_view, name='index'),
    path('panel-principal/', views.panel_principal_view, name='panel_principal'),  # <- NUEVO
    path('dashboard/', views.dashboard_view, name='dashboard'),  # <- Ahora solo gráficos
    path('tickets/', views.ticket_list_view, name='ticket_list'),
    path('tickets/<int:ticket_id>/', views.ticket_list_view, name='ticket_detail'),

    # --- RUTAS DE "MIS TICKETS" (DOCENTE) ---
    path('mis-tickets/', views.mis_tickets_view, name='mis_tickets'),
    path('mis-tickets/<int:ticket_id>/', views.mis_tickets_view, name='mis_tickets_detalle'),

    # --- RUTAS DE "TI" ---
    path('mis-asignaciones/', views.mis_asignaciones_view, name='mis_asignaciones'),
    
    path('mis-asignaciones/<int:ticket_id>/', views.mis_asignaciones_view, name='mis_asignaciones_detalle'),
    path('reportes/', views.reportes_view, name='reportes'),
    path('reportes/descargar-csv/', views.descargar_reporte_csv, name='descargar_reporte_csv'),

    # --- URL DE NOTIFICACIONES ---
    path('notificaciones/', views.notificaciones_view, name='notificaciones'),

    # --- GESTIÓN DE USUARIOS (SUPERADMIN) ---
    path('usuarios/', views.usuarios_list_view, name='usuarios_list'),
    path('usuarios/crear/', views.usuario_create_view, name='usuario_create'),
    path('usuarios/<int:rut>/editar/', views.usuario_edit_view, name='usuario_edit'),
    path('usuarios/<int:rut>/toggle/', views.usuario_toggle_estado_view, name='usuario_toggle_estado'),
    path('usuarios/<int:rut>/detalle/', views.usuario_detail_view, name='usuario_detail'),

    # --- BORRAR TICKET ---
    path('mis-tickets/borrar/<int:ticket_id>/', views.borrar_mi_ticket_view, name='borrar_mi_ticket'),
    path('tickets/borrar/<int:ticket_id>/', views.borrar_ticket_admin_view, name='borrar_ticket_admin'),

    path('accounts/', include('django.contrib.auth.urls')),

    # --- FIJAR TICKET (TI) ---
    path('mis-asignaciones/fijar/<int:ticket_id>/', views.toggle_fijar_ticket_view, name='toggle_fijar_ticket'),
]

if settings.DEBUG or not settings.PRODUCTION:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))
