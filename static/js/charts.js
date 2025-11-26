// ==========================================
// FUNCIONES PARA GRÁFICOS (Chart.js)
// ==========================================

// Función para obtener colores según el tema
function getChartColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    
    return {
        gridColor: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
        textColor: isDark ? '#e8e8f0' : '#1f2430',
        tooltipBg: isDark ? '#1a1a24' : '#fff',
        tooltipBorder: isDark ? '#2a2a3a' : '#e7e8ee'
    };
}

// Configuración global de Chart.js
function initChartDefaults() {
    if (typeof Chart === 'undefined') return;
    
    const colors = getChartColors();
    Chart.defaults.color = colors.textColor;
    Chart.defaults.borderColor = colors.gridColor;
}

// Actualizar charts cuando cambie el tema
window.addEventListener('storage', function(e) {
    if (e.key === 'theme') {
        location.reload();
    }
});

// Inicializar al cargar
document.addEventListener('DOMContentLoaded', initChartDefaults);
