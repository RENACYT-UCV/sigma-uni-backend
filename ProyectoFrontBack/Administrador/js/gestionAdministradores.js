// Gestión de Administradores - JavaScript

class AdminManager {
    constructor() {
        this.admins = this.loadAdmins();
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSampleData();
        this.renderAdminList();
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Form submission
        const nuevoAdminForm = document.getElementById('nuevoAdminForm');
        if (nuevoAdminForm) {
            nuevoAdminForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleNewAdmin(e);
            });
        }

        // Clear form button
        const limpiarBtn = document.getElementById('limpiarForm');
        if (limpiarBtn) {
            limpiarBtn.addEventListener('click', () => {
                this.clearForm('nuevoAdminForm');
            });
        }

        // Search functionality
        const buscarBtn = document.getElementById('buscarBtn');
        if (buscarBtn) {
            buscarBtn.addEventListener('click', () => {
                this.handleSearch();
            });
        }

        const limpiarBusquedaBtn = document.getElementById('limpiarBusquedaBtn');
        if (limpiarBusquedaBtn) {
            limpiarBusquedaBtn.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // Export button
        const exportarBtn = document.getElementById('exportarBtn');
        if (exportarBtn) {
            exportarBtn.addEventListener('click', () => {
                this.exportData();
            });
        }

        // Modal events
        const closeModal = document.getElementById('closeModal');
        if (closeModal) {
            closeModal.addEventListener('click', () => {
                this.closeModal();
            });
        }

        // Close modal on outside click
        const modal = document.getElementById('editModal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        }
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        // Load data if needed
        if (tabName === 'lista') {
            this.renderAdminList();
        }
    }

    handleNewAdmin(e) {
        const formData = new FormData(e.target);
        const adminData = {
            id: Date.now(),
            dni: formData.get('dni'),
            nombres: formData.get('nombres'),
            apellidos: formData.get('apellidos'),
            telefono: formData.get('telefono'),
            email: formData.get('email'),
            direccion: formData.get('direccion'),
            rol: formData.get('rol'),
            estado: formData.get('estado'),
            fechaRegistro: new Date().toLocaleDateString('es-ES')
        };

        // Validate required fields
        if (!adminData.dni || !adminData.nombres || !adminData.apellidos || !adminData.email || !adminData.rol) {
            this.showNotification('Por favor, complete todos los campos obligatorios', 'error');
            return;
        }

        // Check if DNI already exists
        if (this.admins.some(admin => admin.dni === adminData.dni)) {
            this.showNotification('Ya existe un administrador con este DNI', 'error');
            return;
        }

        // Check if email already exists
        if (this.admins.some(admin => admin.email === adminData.email)) {
            this.showNotification('Ya existe un administrador con este email', 'error');
            return;
        }

        // Add admin
        this.admins.push(adminData);
        this.saveAdmins();
        this.clearForm('nuevoAdminForm');
        this.showNotification('Administrador agregado exitosamente', 'success');
        
        // Switch to list tab
        this.switchTab('lista');
    }

    handleSearch() {
        const searchData = {
            dni: document.getElementById('searchDni').value.toLowerCase(),
            nombre: document.getElementById('searchNombre').value.toLowerCase(),
            email: document.getElementById('searchEmail').value.toLowerCase(),
            rol: document.getElementById('searchRol').value,
            estado: document.getElementById('searchEstado').value
        };

        const filteredAdmins = this.admins.filter(admin => {
            return (!searchData.dni || admin.dni.toLowerCase().includes(searchData.dni)) &&
                   (!searchData.nombre || 
                    admin.nombres.toLowerCase().includes(searchData.nombre) ||
                    admin.apellidos.toLowerCase().includes(searchData.nombre)) &&
                   (!searchData.email || admin.email.toLowerCase().includes(searchData.email)) &&
                   (!searchData.rol || admin.rol === searchData.rol) &&
                   (!searchData.estado || admin.estado === searchData.estado);
        });

        this.renderSearchResults(filteredAdmins);
    }

    renderSearchResults(results) {
        const searchResults = document.getElementById('searchResults');
        
        if (results.length === 0) {
            searchResults.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <h3>No se encontraron resultados</h3>
                    <p>Intente con otros criterios de búsqueda</p>
                </div>
            `;
            return;
        }

        const tableHTML = `
            <div class="table-container">
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>DNI/Cédula</th>
                            <th>Nombre Completo</th>
                            <th>Email</th>
                            <th>Rol</th>
                            <th>Estado</th>
                            <th>Fecha Registro</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map(admin => this.createAdminRow(admin)).join('')}
                    </tbody>
                </table>
            </div>
        `;

        searchResults.innerHTML = tableHTML;
        this.attachTableEventListeners();
    }

    clearSearch() {
        document.getElementById('searchDni').value = '';
        document.getElementById('searchNombre').value = '';
        document.getElementById('searchEmail').value = '';
        document.getElementById('searchRol').value = '';
        document.getElementById('searchEstado').value = '';
        document.getElementById('searchResults').innerHTML = '';
    }

    renderAdminList() {
        const tbody = document.getElementById('adminTableBody');
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const paginatedAdmins = this.admins.slice(startIndex, endIndex);

        tbody.innerHTML = paginatedAdmins.map(admin => this.createAdminRow(admin)).join('');
        
        this.renderPagination();
        this.attachTableEventListeners();
    }

    createAdminRow(admin) {
        return `
            <tr>
                <td>${admin.dni}</td>
                <td>${admin.nombres} ${admin.apellidos}</td>
                <td>${admin.email}</td>
                <td><span class="role-badge ${admin.rol}">${this.getRoleName(admin.rol)}</span></td>
                <td><span class="status-badge ${admin.estado}">${admin.estado}</span></td>
                <td>${admin.fechaRegistro}</td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn edit" onclick="adminManager.editAdmin(${admin.id})" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-btn delete" onclick="adminManager.deleteAdmin(${admin.id})" title="Eliminar">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    getRoleName(rol) {
        const roles = {
            'super_admin': 'Super Admin',
            'admin': 'Administrador',
            'moderador': 'Moderador'
        };
        return roles[rol] || rol;
    }

    renderPagination() {
        const pagination = document.getElementById('pagination');
        const totalPages = Math.ceil(this.admins.length / this.itemsPerPage);
        
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        let paginationHTML = `
            <button class="pagination-btn" ${this.currentPage === 1 ? 'disabled' : ''} 
                    onclick="adminManager.changePage(${this.currentPage - 1})">
                <i class="fas fa-chevron-left"></i>
            </button>
        `;

        for (let i = 1; i <= totalPages; i++) {
            paginationHTML += `
                <button class="pagination-btn ${i === this.currentPage ? 'active' : ''}" 
                        onclick="adminManager.changePage(${i})">
                    ${i}
                </button>
            `;
        }

        paginationHTML += `
            <button class="pagination-btn" ${this.currentPage === totalPages ? 'disabled' : ''} 
                    onclick="adminManager.changePage(${this.currentPage + 1})">
                <i class="fas fa-chevron-right"></i>
            </button>
        `;

        pagination.innerHTML = paginationHTML;
    }

    changePage(page) {
        const totalPages = Math.ceil(this.admins.length / this.itemsPerPage);
        if (page >= 1 && page <= totalPages) {
            this.currentPage = page;
            this.renderAdminList();
        }
    }

    attachTableEventListeners() {
        // Event listeners are attached via onclick in the HTML for simplicity
        // In a production environment, you might want to use event delegation
    }

    editAdmin(id) {
        const admin = this.admins.find(a => a.id === id);
        if (!admin) return;

        const modal = document.getElementById('editModal');
        const modalBody = modal.querySelector('.modal-body');
        
        modalBody.innerHTML = `
            <form class="admin-form" id="editAdminForm">
                <input type="hidden" name="id" value="${admin.id}">
                <div class="form-row">
                    <div class="form-group full-width">
                        <label for="editDni">DNI/CÉDULA *</label>
                        <input type="text" id="editDni" name="dni" value="${admin.dni}" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="editNombres">Nombres *</label>
                        <input type="text" id="editNombres" name="nombres" value="${admin.nombres}" required>
                    </div>
                    <div class="form-group">
                        <label for="editApellidos">Apellidos *</label>
                        <input type="text" id="editApellidos" name="apellidos" value="${admin.apellidos}" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="editTelefono">Teléfono</label>
                        <input type="tel" id="editTelefono" name="telefono" value="${admin.telefono || ''}">
                    </div>
                    <div class="form-group">
                        <label for="editEmail">Email *</label>
                        <input type="email" id="editEmail" name="email" value="${admin.email}" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group full-width">
                        <label for="editDireccion">Dirección</label>
                        <input type="text" id="editDireccion" name="direccion" value="${admin.direccion || ''}">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="editRol">Rol de Administrador *</label>
                        <select id="editRol" name="rol" required>
                            
                            <option value="admin" ${admin.rol === 'admin' ? 'selected' : ''}>Administrador</option>
                            
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="editEstado">Estado *</label>
                        <select id="editEstado" name="estado" required>
                            <option value="activo" ${admin.estado === 'activo' ? 'selected' : ''}>Activo</option>
                            <option value="inactivo" ${admin.estado === 'inactivo' ? 'selected' : ''}>Inactivo</option>
                        </select>
                    </div>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="adminManager.closeModal()">
                        <i class="fas fa-times"></i>
                        Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i>
                        Actualizar
                    </button>
                </div>
            </form>
        `;

        // Add form submit listener
        const editForm = document.getElementById('editAdminForm');
        editForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleEditAdmin(e);
        });

        modal.classList.add('active');
    }

    handleEditAdmin(e) {
        const formData = new FormData(e.target);
        const adminId = parseInt(formData.get('id'));
        const adminIndex = this.admins.findIndex(a => a.id === adminId);
        
        if (adminIndex === -1) return;

        const updatedAdmin = {
            ...this.admins[adminIndex],
            dni: formData.get('dni'),
            nombres: formData.get('nombres'),
            apellidos: formData.get('apellidos'),
            telefono: formData.get('telefono'),
            email: formData.get('email'),
            direccion: formData.get('direccion'),
            rol: formData.get('rol'),
            estado: formData.get('estado')
        };

        // Validate required fields
        if (!updatedAdmin.dni || !updatedAdmin.nombres || !updatedAdmin.apellidos || !updatedAdmin.email || !updatedAdmin.rol) {
            this.showNotification('Por favor, complete todos los campos obligatorios', 'error');
            return;
        }

        // Check if DNI already exists (excluding current admin)
        if (this.admins.some(admin => admin.dni === updatedAdmin.dni && admin.id !== adminId)) {
            this.showNotification('Ya existe un administrador con este DNI', 'error');
            return;
        }

        // Check if email already exists (excluding current admin)
        if (this.admins.some(admin => admin.email === updatedAdmin.email && admin.id !== adminId)) {
            this.showNotification('Ya existe un administrador con este email', 'error');
            return;
        }

        this.admins[adminIndex] = updatedAdmin;
        this.saveAdmins();
        this.renderAdminList();
        this.closeModal();
        this.showNotification('Administrador actualizado exitosamente', 'success');
    }

    deleteAdmin(id) {
        if (confirm('¿Está seguro de que desea eliminar este administrador?')) {
            this.admins = this.admins.filter(admin => admin.id !== id);
            this.saveAdmins();
            this.renderAdminList();
            this.showNotification('Administrador eliminado exitosamente', 'success');
        }
    }

    closeModal() {
        const modal = document.getElementById('editModal');
        modal.classList.remove('active');
    }

    clearForm(formId) {
        const form = document.getElementById(formId);
        if (form) {
            form.reset();
        }
    }

    exportData() {
        const csvContent = this.generateCSV();
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `administradores_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showNotification('Datos exportados exitosamente', 'success');
    }

    generateCSV() {
        const headers = ['DNI/Cédula', 'Nombres', 'Apellidos', 'Email', 'Teléfono', 'Dirección', 'Rol', 'Estado', 'Fecha Registro'];
        const csvRows = [headers.join(',')];
        
        this.admins.forEach(admin => {
            const row = [
                admin.dni,
                admin.nombres,
                admin.apellidos,
                admin.email,
                admin.telefono || '',
                admin.direccion || '',
                this.getRoleName(admin.rol),
                admin.estado,
                admin.fechaRegistro
            ];
            csvRows.push(row.join(','));
        });
        
        return csvRows.join('\n');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        // Add styles if not already added
        if (!document.querySelector('#notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 1rem 1.5rem;
                    border-radius: 0.5rem;
                    color: white;
                    font-weight: 600;
                    z-index: 3000;
                    animation: slideInRight 0.3s ease-in-out;
                    max-width: 400px;
                }
                .notification.success { background: var(--success-color); }
                .notification.error { background: var(--danger-color); }
                .notification.info { background: var(--accent-color); }
                .notification-content {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }

        document.body.appendChild(notification);

        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideInRight 0.3s ease-in-out reverse';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    loadSampleData() {
        if (this.admins.length === 0) {
            this.admins = [
                {
                    id: 1,
                    dni: '12345678',
                    nombres: 'Juan Carlos',
                    apellidos: 'Pérez García',
                    telefono: '+57 300 123 4567',
                    email: 'juan.perez@sigma.com',
                    direccion: 'Calle 123 #45-67, Bogotá',
                    rol: 'admin',
                    estado: 'activo',
                    fechaRegistro: '15/01/2024'
                },
                {
                    id: 2,
                    dni: '87654321',
                    nombres: 'María Elena',
                    apellidos: 'González López',
                    telefono: '+57 310 987 6543',
                    email: 'maria.gonzalez@sigma.com',
                    direccion: 'Carrera 45 #12-34, Medellín',
                    rol: 'admin',
                    estado: 'activo',
                    fechaRegistro: '20/01/2024'
                },
                {
                    id: 3,
                    dni: '11223344',
                    nombres: 'Carlos Alberto',
                    apellidos: 'Rodríguez Martínez',
                    telefono: '+57 320 456 7890',
                    email: 'carlos.rodriguez@sigma.com',
                    direccion: 'Avenida 80 #23-45, Cali',
                    rol: 'admin',
                    estado: 'inactivo',
                    fechaRegistro: '25/01/2024'
                }
            ];
            this.saveAdmins();
        }
    }

    loadAdmins() {
        const stored = localStorage.getItem('sigma_admins');
        return stored ? JSON.parse(stored) : [];
    }

    saveAdmins() {
        localStorage.setItem('sigma_admins', JSON.stringify(this.admins));
    }
}

// Initialize the admin manager when the page loads
let adminManager;
document.addEventListener('DOMContentLoaded', () => {
    adminManager = new AdminManager();
});