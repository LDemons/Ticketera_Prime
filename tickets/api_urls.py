"""
URLs para la API REST de Ticketera Prime
Define todos los endpoints disponibles para la aplicación móvil
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    TicketViewSet, NotificacionViewSet, 
    CustomAuthToken, CategoriaListView, PrioridadListView,
    user_profile, dashboard_stats, change_password
)

# Router para ViewSets (genera automáticamente las URLs CRUD)
router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='api-ticket')
router.register(r'notificaciones', NotificacionViewSet, basename='api-notificacion')

# URLs de la API
urlpatterns = [
    # ==========================================
    # AUTENTICACIÓN
    # ==========================================
    path('auth/login/', CustomAuthToken.as_view(), name='api-login'),
    path('auth/profile/', user_profile, name='api-profile'),
    path('auth/change-password/', change_password, name='api-change-password'),
    
    # ==========================================
    # DATOS AUXILIARES PARA CREAR TICKETS
    # ==========================================
    path('categorias/', CategoriaListView.as_view(), name='api-categorias'),
    path('prioridades/', PrioridadListView.as_view(), name='api-prioridades'),
    
    # ==========================================
    # ESTADÍSTICAS
    # ==========================================
    path('stats/', dashboard_stats, name='api-stats'),
    
    # ==========================================
    # ROUTER (TICKETS, NOTIFICACIONES, ETC.)
    # ==========================================
    # Esto incluye:
    # - GET/POST /tickets/
    # - GET/PUT/PATCH/DELETE /tickets/{id}/
    # - POST /tickets/{id}/add_comment/
    # - POST /tickets/{id}/toggle_pin/
    # - GET /notificaciones/
    # - GET /notificaciones/{id}/
    # - POST /notificaciones/{id}/mark_read/
    # - POST /notificaciones/mark_all_read/
    path('', include(router.urls)),
]
