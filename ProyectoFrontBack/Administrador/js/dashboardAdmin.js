document.addEventListener('DOMContentLoaded', () => {
    console.log("DOMContentLoaded cargado");

    // Elementos del DOM
    const sidebar = document.getElementById('sidebar');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileOverlay = document.getElementById('mobileOverlay');
    const navLinks = document.querySelectorAll('.nav-link');
    const contentAreas = document.querySelectorAll('.content-area');
    const usuariosCounter = document.querySelector('.stat-number');

    // Función para obtener datos desde un endpoint
    async function fetchData(endpoint) {
        const res = await fetch(endpoint);
        if (!res.ok) throw new Error(`Error en la petición: ${res.status}`);
        return await res.json();
    }

    // Contador animado
    function animarContador(element, target) {
        let current = 0;
        const step = target / 100;
        const interval = setInterval(() => {
            current += step;
            if (current >= target) {
                element.textContent = target;
                clearInterval(interval);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 15);
    }

    // Construir gráfico
    function buildChart(ctx, label, labels, data, color, type = 'line') {
        return new Chart(ctx, {
            type: type,
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: data,
                    backgroundColor: color + '33',
                    borderColor: color,
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    // Cargar gráfico de usuarios y puntajes
    async function cargarGraficosDashboard() {
        try {
            const modoPuntaje = 'semana';
            const modoUsuarios = 'mensual';

            const datosPuntaje = await fetchData(`/api/dashboard/puntajes?modo=${modoPuntaje}`);
            const datosUsuarios = await fetchData(`/api/dashboard/usuarios?modo=${modoUsuarios}`);

            const fechasPuntaje = datosPuntaje.map(d => d.fecha);
            const valoresPuntaje = datosPuntaje.map(d => d.cantidad);

            const fechasUsuarios = datosUsuarios.map(d => d.fecha);
            const valoresUsuarios = datosUsuarios.map(d => d.cantidad);

            buildChart(document.getElementById('scoresChart'), 'Puntajes completados', fechasPuntaje, valoresPuntaje, '#4e73df');
            buildChart(document.getElementById('usersChart'), 'Usuarios nuevos', fechasUsuarios, valoresUsuarios, '#1cc88a');
        } catch (error) {
            console.error("Error al cargar gráficos:", error);
        }
    }

    // Cargar tabla de usuarios
    async function cargarUsuarios() {
        try {
            const data = await fetchData('/api/usuarios');
            console.log("Usuarios:", data);

            if (!Array.isArray(data)) {
                throw new Error("La respuesta no es una lista de usuarios");
            }

            const tabla = document.getElementById('tablaUsuarios');
            tabla.innerHTML = "";
            data.forEach(usuario => {
                tabla.innerHTML += `
                    <tr>
                        <td>${usuario.nombre}</td>
                        <td>${usuario.email}</td>
                    </tr>
                `;
            });

            // Contador de usuarios
            if (usuariosCounter && !isNaN(data.length)) {
                animarContador(usuariosCounter, data.length);
            }

        } catch (err) {
            console.error("Error al cargar usuarios:", err);
        }
    }

    // Mostrar sección
    const switchContent = (targetSection) => {
        contentAreas.forEach(area => area.classList.add('hidden'));
        const targetContent = document.getElementById(targetSection + 'Content');
        if (targetContent) targetContent.classList.remove('hidden');

        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        const activeNavItem = document.querySelector(`[data-section="${targetSection}"]`)?.closest('.nav-item');
        if (activeNavItem) activeNavItem.classList.add('active');

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

        if (targetSection === 'usuarios') cargarUsuarios();
        if (window.innerWidth <= 768) closeSidebar();
    };

    // Sidebar
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

    // Listeners
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.getAttribute('data-section');
            if (section) switchContent(section);
        });
    });

    if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', toggleSidebar);
    if (mobileOverlay) mobileOverlay.addEventListener('click', closeSidebar);

    // Inicial
    switchContent('dashboard');
    cargarUsuarios();
    cargarGraficosDashboard();
});
