// ==========================================
// FUNCIONES DE TICKETS
// ==========================================

// Función para manejar clic en botón de gestionar (desktop vs móvil)
function handleTicketClick(element, event) {
    console.log('Ancho de pantalla:', window.innerWidth);
    // En móvil (<= 768px), permitir navegación normal al detalle completo
    if (window.innerWidth <= 768) {
        console.log('MÓVIL: Navegando a página completa');
        return true; // Navegar a la página de detalle
    }
    
    // En desktop (> 768px), prevenir navegación y abrir panel lateral
    console.log('DESKTOP: Abriendo panel lateral');
    event.preventDefault();
    const ticketId = element.getAttribute('data-ticket-id');
    const estado = new URLSearchParams(window.location.search).get('estado') || 'todos';
    const orden = new URLSearchParams(window.location.search).get('orden') || 'reciente';
    
    // Obtener la URL base del href del elemento
    const href = element.getAttribute('href');
    const baseUrl = href.substring(0, href.indexOf(ticketId));
    
    window.location.href = `${baseUrl}${ticketId}/?estado=${estado}&orden=${orden}`;
    return false;
}

// Función para manejar clic en tickets del panel admin (desktop vs móvil)
function handleTicketClickAdmin(element, event) {
    // En móvil (<= 768px), permitir navegación normal al detalle completo
    if (window.innerWidth <= 768) {
        return true; // Navegar a ticket_detail_full
    }
    
    // En desktop (> 768px), prevenir navegación y abrir panel lateral
    event.preventDefault();
    const ticketId = element.getAttribute('data-ticket-id');
    const estado = new URLSearchParams(window.location.search).get('estado') || 'todos';
    const orden = new URLSearchParams(window.location.search).get('orden') || 'reciente';
    
    // Redirigir a la vista con panel lateral (sin /detalle/)
    window.location.href = `/tickets/${ticketId}/?estado=${estado}&orden=${orden}`;
    return false;
}

// Toggle del menú de opciones (3 puntos) en tickets
document.addEventListener('DOMContentLoaded', function() {
    const menuToggles = document.querySelectorAll('.ticket-menu-toggle');
    
    menuToggles.forEach(toggle => {
        toggle.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            
            const menu = this.nextElementSibling;
            const isVisible = menu.style.display === 'block';
            
            // Cerrar todos los menús abiertos
            document.querySelectorAll('.ticket-dropdown-menu').forEach(m => m.style.display = 'none');
            
            // Abrir/cerrar el menú actual
            menu.style.display = isVisible ? 'none' : 'block';
        });
    });

    // Cerrar menús al hacer clic fuera
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.ticket-menu-wrapper')) {
            document.querySelectorAll('.ticket-dropdown-menu').forEach(m => m.style.display = 'none');
        }
    });
});

// Auto-scroll al último mensaje en el chat del panel de detalle
document.addEventListener('DOMContentLoaded', function() {
    const detailBody = document.querySelector('.detail-body');
    if (detailBody) {
        // Scroll al final cuando se carga la página
        detailBody.scrollTop = detailBody.scrollHeight;
        
        // Observer para scroll automático cuando se agregan nuevos mensajes
        const observer = new MutationObserver(function() {
            detailBody.scrollTop = detailBody.scrollHeight;
        });
        
        observer.observe(detailBody, {
            childList: true,
            subtree: true
        });
    }
});
