
import random
from tickets.models import Ticket, Usuario, Prioridad, Categoria



def run():
    print("Borrando tickets antiguos...")
    Ticket.objects.all().delete()

    print("Obteniendo datos para crear tickets...")
    # Obtenemos un usuario creador (el primero que encuentre)
    try:
        creador = Usuario.objects.first()
        if not creador:
            print("Error: No hay usuarios en la base de datos. Por favor, crea uno.")
            return
    except Usuario.DoesNotExist:
        print("Error: El modelo Usuario no existe o no se puede acceder.")
        return

    # Obtenemos todas las prioridades y categorías disponibles
    prioridades = list(Prioridad.objects.all())
    categorias = list(Categoria.objects.all())

    if not prioridades or not categorias:
        print("Error: Debes tener al menos una Prioridad y una Categoria en la BD.")
        return

    print(f"Creando tickets para el usuario: {creador.nombre}")

    # --- Lista de Títulos y Descripciones de ejemplo ---
    titulos_ejemplo = [
        "Problema con proyector en sala 101",
        "No puedo acceder a la red WiFi de la escuela",
        "El mouse de mi computador no funciona",
        "Necesito instalación del software 'Geogebra'",
        "La impresora del segundo piso no tiene tinta",
        "La pantalla de mi notebook se ve con rayas",
        "No recuerdo mi contraseña del portal de notas",
        "El audio no funciona en el laboratorio de computación",
        "Solicitud de acceso a carpeta compartida de 'Ciencias'",
        "El computador de la biblioteca está muy lento",
    ]

    descripciones_ejemplo = [
        "El proyector no enciende al conectarlo al notebook.",
        "Intento conectarme a la red 'ColegioNet' pero me da error de autenticación.",
        "He probado en distintos puertos USB pero el cursor no se mueve.",
        "Requiero el software para mis clases de matemática. Es de uso libre.",
        "He intentado imprimir un documento y la hoja sale en blanco.",
        "Aparecen líneas verticales de colores en la pantalla, sobre todo al moverla.",
        "He intentado restablecerla pero no me llega el correo de recuperación.",
        "Ninguno de los audífonos del laboratorio parece funcionar.",
        "Necesito acceder a los archivos de planificación del departamento de Ciencias.",
        "Tarda mucho en abrir programas básicos como el navegador o Word."
    ]

    print("Iniciando la creación de 10 tickets de prueba...")

    for i in range(10):
        ticket = Ticket(
            titulo=random.choice(titulos_ejemplo),
            descripcion=random.choice(descripciones_ejemplo),
            usuario_creador=creador,
            prioridad=random.choice(prioridades),
            categoria=random.choice(categorias),
            estado=random.choice(['ABIERTO', 'EN_PROGRESO', 'RESUELTO'])
        )
        ticket.save()

    print("¡Listo! Se han creado 10 tickets de prueba en la base de datos.")