// ==========================================
// MENÚ DE USUARIO Y SIDEBAR
// ==========================================

// Toggle del menú de usuario
function toggleUserMenu(event) {
    if (event) {
        event.stopPropagation();
    }
    const menu = document.getElementById('userMenu');
    const isVisible = menu.style.display === 'block';
    
    if (isVisible) {
        menu.style.display = 'none';
    } else {
        menu.style.display = 'block';
        menu.style.visibility = 'visible';
        menu.style.opacity = '1';
    }
}

// Función para cerrar sidebar en móvil
function closeSidebarMobile() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    if (sidebar && overlay) {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
    }
}

// Cerrar menú al hacer clic fuera
document.addEventListener('click', function(event) {
    const userProfile = document.querySelector('.user-profile');
    const userMenu = document.getElementById('userMenu');
    
    if (userProfile && !userProfile.contains(event.target) && userMenu && !userMenu.contains(event.target)) {
        userMenu.style.display = 'none';
    }
});

// --- Menú móvil ---
document.addEventListener('DOMContentLoaded', function() {
    // Crear botón de menú móvil
    const menuToggle = document.createElement('button');
    menuToggle.className = 'mobile-menu-toggle';
    menuToggle.setAttribute('aria-label', 'Abrir menú');
    menuToggle.innerHTML = '<svg viewBox="0 0 24 24" style="width: 24px; height: 24px; stroke: currentColor; fill: none; stroke-width: 2;"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>';
    document.body.insertBefore(menuToggle, document.body.firstChild);

    // Crear overlay
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.insertBefore(overlay, document.body.firstChild);

    const sidebar = document.querySelector('.sidebar');

    // Toggle del sidebar
    function toggleSidebar() {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
        
        // Cambiar ícono
        if (sidebar.classList.contains('active')) {
            menuToggle.innerHTML = '<svg viewBox="0 0 24 24" style="width: 24px; height: 24px; stroke: currentColor; fill: none; stroke-width: 2;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
            menuToggle.setAttribute('aria-label', 'Cerrar menú');
        } else {
            menuToggle.innerHTML = '<svg viewBox="0 0 24 24" style="width: 24px; height: 24px; stroke: currentColor; fill: none; stroke-width: 2;"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>';
            menuToggle.setAttribute('aria-label', 'Abrir menú');
        }
    }

    menuToggle.addEventListener('click', toggleSidebar);
    overlay.addEventListener('click', toggleSidebar);

    // Cerrar sidebar al hacer clic en un enlace (en móvil)
    const sidebarLinks = sidebar.querySelectorAll('a');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
                menuToggle.innerHTML = '<svg viewBox="0 0 24 24" style="width: 24px; height: 24px; stroke: currentColor; fill: none; stroke-width: 2;"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>';
            }
        });
    });
});
