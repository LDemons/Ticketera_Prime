"""
Backend de autenticación personalizado para permitir login con email
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailBackend(ModelBackend):
    """
    Backend de autenticación que permite login con email en lugar de username
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Buscar usuario por email (case-insensitive)
            # El campo 'username' viene del form pero contiene el email
            user = User.objects.get(email__iexact=username)
            
            # Verificar contraseña
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Si hay múltiples usuarios con el mismo email, retornar None
            return None
        
        return None
