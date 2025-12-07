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

// Modal para cambiar contraseña
function mostrarModalCambiarContrasenia() {
    Swal.fire({
        title: 'Cambiar Contraseña',
        html: `
            <div style="text-align: left;">
                <label style="display: block; margin-bottom: 15px;">
                    <span style="font-weight: 600; margin-bottom: 5px; display: block; font-size: 14px;">Contraseña Actual:</span>
                    <input type="password" id="swal-contrasenia-actual" class="swal2-input" placeholder="Tu contraseña actual" style="width: 100%; margin: 0;">
                </label>
                <label style="display: block; margin-bottom: 15px;">
                    <span style="font-weight: 600; margin-bottom: 5px; display: block; font-size: 14px;">Nueva Contraseña:</span>
                    <input type="password" id="swal-nueva-contrasenia" class="swal2-input" placeholder="Mínimo 6 caracteres" style="width: 100%; margin: 0;">
                </label>
                <label style="display: block; margin-bottom: 10px;">
                    <span style="font-weight: 600; margin-bottom: 5px; display: block; font-size: 14px;">Confirmar Nueva Contraseña:</span>
                    <input type="password" id="swal-confirmar-contrasenia" class="swal2-input" placeholder="Repite la nueva contraseña" style="width: 100%; margin: 0;">
                </label>
            </div>
        `,
        showCancelButton: true,
        confirmButtonText: 'Cambiar Contraseña',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#2a0441',
        width: '500px',
        preConfirm: () => {
            const actual = document.getElementById('swal-contrasenia-actual').value;
            const nueva = document.getElementById('swal-nueva-contrasenia').value;
            const confirmar = document.getElementById('swal-confirmar-contrasenia').value;
            
            // Validaciones
            if (!actual || actual.trim() === '') {
                Swal.showValidationMessage('Por favor ingresa tu contraseña actual');
                return false;
            }
            
            if (!nueva || nueva.trim() === '') {
                Swal.showValidationMessage('Por favor ingresa una nueva contraseña');
                return false;
            }
            
            if (nueva.length < 6) {
                Swal.showValidationMessage('La contraseña debe tener al menos 6 caracteres');
                return false;
            }
            
            if (nueva !== confirmar) {
                Swal.showValidationMessage('Las contraseñas nuevas no coinciden');
                return false;
            }
            
            return { 
                contrasenia_actual: actual, 
                nueva_contrasenia: nueva,
                confirmar_contrasenia: confirmar
            };
        }
    }).then((result) => {
        if (result.isConfirmed) {
            // Obtener el token CSRF
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Hacer la petición AJAX
            fetch('/cambiar-contrasenia-ajax/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(result.value)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Contraseña actualizada!',
                        text: 'Tu contraseña ha sido cambiada exitosamente',
                        confirmButtonColor: '#2a0441'
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: data.error || 'No se pudo cambiar la contraseña',
                        confirmButtonColor: '#d33'
                    });
                }
            })
            .catch(error => {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Ocurrió un error al cambiar la contraseña',
                    confirmButtonColor: '#d33'
                });
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
