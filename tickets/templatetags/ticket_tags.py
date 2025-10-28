from django import template

register = template.Library()

@register.filter(name='split_at_hash')
def split_at_hash(value):
    """
    Parte un string en el primer '#' y devuelve una lista.
    Volvemos a añadir el '#' a la segunda parte.
    """
    if '#' in value:
        parts = value.split('#', 1)
        # parts[0] = "Se te ha asignado el ticket "
        # parts[1] = "T031: 'teste 111...'"
        return [parts[0], '#' + parts[1]]
    else:
        # Si no hay '#', solo devuelve el texto original en una lista
        return [value]