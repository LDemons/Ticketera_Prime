// ==========================================
// MODALES Y ALERTAS
// ==========================================

// Modal para editar perfil
function mostrarModalPerfil() {
    Swal.fire({
        title: 'Editar Nombre',
        html: `
            <div style="text-align: left;">
                <label style="display: block; margin-bottom: 10px;">
                    <span style="font-weight: 600; margin-bottom: 5px; display: block;">Nombre:</span>
                    <input id="swal-nombre" class="swal2-input" placeholder="Tu nombre" style="width: 100%; margin: 0;">
                </label>
            </div>
        `,
        showCancelButton: true,
        confirmButtonText: 'Guardar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#2a0441',
        preConfirm: () => {
            const nombre = document.getElementById('swal-nombre').value;
            if (!nombre || nombre.trim() === '') {
                Swal.showValidationMessage('Por favor ingresa un nombre');
                return false;
            }
            return { nombre: nombre };
        }
    }).then((result) => {
        if (result.isConfirmed) {
            // Aquí podrías hacer una llamada AJAX para guardar los cambios
            // Por ahora solo mostramos un mensaje de confirmación
            Swal.fire({
                icon: 'success',
                title: 'Nombre actualizado',
                text: 'Los cambios se han guardado correctamente',
                confirmButtonColor: '#2a0441'
            }).then(() => {
                // Recarga la página para ver los cambios
                location.reload();
            });
        }
    });
}

// Confirmación para borrar tickets
document.addEventListener('DOMContentLoaded', function() {
    const formsBorrar = document.querySelectorAll('.form-borrar');
    
    formsBorrar.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            Swal.fire({
                title: '¿Estás seguro?',
                text: "Esta acción no se puede deshacer",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Sí, borrar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit();
                }
            });
        });
    });
});
