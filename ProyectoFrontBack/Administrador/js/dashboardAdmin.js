// DOM Elements
const sidebar = document.getElementById('sidebar');
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const mobileOverlay = document.getElementById('mobileOverlay');
const navLinks = document.querySelectorAll('.nav-link');
const contentAreas = document.querySelectorAll('.content-area');

// Utility Functions
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// Sidebar Functions
const toggleSidebar = () => {
    sidebar.classList.toggle('active');
    mobileOverlay.classList.toggle('active');
    document.body.style.overflow = sidebar.classList.contains('active') ? 'hidden' : '';
};

const closeSidebar = () => {
    sidebar.classList.remove('active');
    mobileOverlay.classList.remove('active');
    document.body.style.overflow = '';
};

// Navigation Functions
const switchContent = (targetSection) => {
    // Hide all content areas
    contentAreas.forEach(area => {
        area.classList.add('hidden');
    });
    
    // Show target content area
    const targetContent = document.getElementById(targetSection + 'Content');
    if (targetContent) {
        targetContent.classList.remove('hidden');
    }
    
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const activeNavItem = document.querySelector(`[data-section="${targetSection}"]`).closest('.nav-item');
    if (activeNavItem) {
        activeNavItem.classList.add('active');
    }
    
    // Update page title
    const pageTitle = document.querySelector('.page-title');
    const sectionTitles = {
        dashboard: 'Dashboard',
        usuarios: 'Gestión de Usuarios',
        lecciones: 'Gestión de Lecciones',
        progreso: 'Seguimiento de Progreso',
        reportes: 'Reportes y Análisis',
        configuracion: 'Configuración del Sistema'
    };
    
    pageTitle.textContent = sectionTitles[targetSection] || 'Dashboard';
    
    // Close sidebar on mobile after navigation
    if (window.innerWidth <= 768) {
        closeSidebar();
    }
};

// Animation Functions
const animateCounter = (element, target, duration = 2000) => {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        element.textContent = Math.floor(current);
        
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        }
    }, 16);
};

const animateCounters = () => {
    const counters = document.querySelectorAll('.stat-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.dataset.target);
                animateCounter(entry.target, target);
                observer.unobserve(entry.target);
            }
        });
    });
    
    counters.forEach(counter => {
        observer.observe(counter);
    });
};

// Chart Functions
const initializeCharts = () => {
    // Scores Chart (Bar Chart)
    const scoresCtx = document.getElementById('scoresChart');
    if (scoresCtx) {
        const scoresChart = new Chart(scoresCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
                datasets: [{
                    label: 'Puntaje Promedio',
                    data: [75, 82, 68, 90, 85, 78, 88],
                    backgroundColor: 'rgba(52, 152, 219, 0.8)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(44, 62, 80, 0.9)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: 'rgba(52, 152, 219, 1)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            color: '#7f8c8d'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#7f8c8d'
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }
    
    // Users Chart (Line Chart)
    const usersCtx = document.getElementById('usersChart');
    if (usersCtx) {
        const usersChart = new Chart(usersCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                datasets: [{
                    label: 'Usuarios Activos',
                    data: [120, 190, 300, 500, 200, 300, 450, 600, 750, 900, 1100, 1247],
                    borderColor: 'rgba(39, 174, 96, 1)',
                    backgroundColor: 'rgba(39, 174, 96, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: 'rgba(39, 174, 96, 1)',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(44, 62, 80, 0.9)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: 'rgba(39, 174, 96, 1)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            color: '#7f8c8d'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#7f8c8d'
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }
};

// Search Functionality
const initializeSearch = () => {
    const searchInput = document.querySelector('.search-box input');
    
    if (searchInput) {
        const debouncedSearch = debounce((query) => {
            console.log('Buscando:', query);
            // Aquí puedes implementar la lógica de búsqueda
        }, 300);
        
        searchInput.addEventListener('input', (e) => {
            debouncedSearch(e.target.value);
        });
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    animateCounters();
    initializeCharts();
    initializeSearch();
    
    // Mobile menu events
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', toggleSidebar);
    }
    
    if (mobileOverlay) {
        mobileOverlay.addEventListener('click', closeSidebar);
    }
    
    // js/dashboardAdmin.js

// Navigation events
const navLinks = document.querySelectorAll('.nav-link');

navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        const href = link.getAttribute('href');
        
        // Si es un enlace externo (a otra página), permitir navegación normal
        if (href && href.endsWith('.html')) {
            // Permitir navegación normal
            return;
        }
        
        // Si es navegación interna, prevenir default y cambiar sección
        e.preventDefault();
        const section = link.dataset.section;
        if (section) {
            switchContent(section);
        }
    });
});

function switchContent(section) {
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(s => s.classList.remove('active'));

    const targetSection = document.getElementById(section);
    if (targetSection) {
        targetSection.classList.add('active');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Logout button
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (confirm('¿Está seguro de que desea cerrar sesión?')) {
                // Aquí puedes añadir la lógica de logout
                // Por ejemplo, limpiar localStorage, redirigir a login, etc.
                alert('Sesión cerrada exitosamente');
                // window.location.href = 'login.html'; // Descomenta cuando tengas página de login
            }
        });
    }
});
    
    // Chart filter events
    document.querySelectorAll('.chart-filter').forEach(filter => {
        filter.addEventListener('change', (e) => {
            console.log(`Filtro cambiado a: ${e.target.value}`);
            // Aquí puedes implementar la lógica para actualizar los gráficos
        });
    });
    
    // Responsive handling
    const handleResize = debounce(() => {
        if (window.innerWidth > 768) {
            closeSidebar();
        }
    }, 250);
    
    window.addEventListener('resize', handleResize);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Escape to close sidebar on mobile
        if (e.key === 'Escape') {
            closeSidebar();
        }
        
        // Ctrl/Cmd + K for search focus (only on desktop)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k' && window.innerWidth > 768) {
            e.preventDefault();
            const searchInput = document.querySelector('.search-box input');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });
});

// Export functions for potential use
window.SigmaAdmin = {
    switchContent,
    toggleSidebar,
    closeSidebar
};
