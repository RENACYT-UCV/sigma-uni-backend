// Gestión de Usuarios - JavaScript

class UserManager {
    constructor() {
        this.users = this.loadUsers();
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSampleData();
        this.renderUserList();
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Save user button
        const guardarUsuarioBtn = document.getElementById('guardarUsuario');
        if (guardarUsuarioBtn) {
            guardarUsuarioBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleNewUser();
            });
        }

        // Clear form button
        const limpiarBtn = document.getElementById('limpiarForm');
        if (limpiarBtn) {
            limpiarBtn.addEventListener('click', () => {
                this.clearAllForms();
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

        // Password confirmation validation
        const confirmarContrasena = document.getElementById('confirmarContrasena');
        if (confirmarContrasena) {
            confirmarContrasena.addEventListener('blur', () => {
                this.validatePasswordMatch();
            });
        }

        // Date of birth change event to calculate age
        const fechaNacimiento = document.getElementById('fechaNacimiento');
        if (fechaNacimiento) {
            fechaNacimiento.addEventListener('change', () => {
                this.calculateAge();
            });
        }
    }

    calculateAge() {
        const fechaNacimiento = document.getElementById('fechaNacimiento').value;
        const edadInput = document.getElementById('edad');
        
        if (fechaNacimiento) {
            const birthDate = new Date(fechaNacimiento);
            const today = new Date();
            let age = today.getFullYear() - birthDate.getFullYear();
            const monthDiff = today.getMonth() - birthDate.getMonth();
            
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }
            
            // Validar que la edad sea razonable
            if (age < 0) {
                edadInput.value = '';
                this.showNotification('La fecha de nacimiento no puede ser futura', 'error');
                return;
            }
            
            if (age > 120) {
                edadInput.value = '';
                this.showNotification('Por favor, verifique la fecha de nacimiento', 'error');
                return;
            }
            
            edadInput.value = age;
        } else {
            edadInput.value = '';
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
            this.renderUserList();
        }
    }

    validatePasswordMatch() {
        const password = document.getElementById('contrasena').value;
        const confirmPassword = document.getElementById('confirmarContrasena').value;
        const confirmInput = document.getElementById('confirmarContrasena');

        if (password && confirmPassword && password !== confirmPassword) {
            confirmInput.style.borderColor = 'var(--danger-color)';
            this.showNotification('Las contraseñas no coinciden', 'error');
            return false;
        } else {
            confirmInput.style.borderColor = 'var(--border-color)';
            return true;
        }
    }

    handleNewUser() {
        // Get data from both forms
        const personalData = this.getFormData('nuevoUsuarioForm');
        const accountData = this.getFormData('datosUsuarioForm');
        
        // Validate password match
        if (!this.validatePasswordMatch()) {
            return;
        }

        // Calculate age from birth date
        const edad = this.calculateAgeFromDate(personalData.fechaNacimiento);
        
        const userData = {
            id: Date.now(),
            ...personalData,
            ...accountData,
            edad: edad,
            fechaRegistro: new Date().toLocaleDateString('es-ES')
        };

        // Validate required fields
        if (!userData.dni || !userData.nombres || !userData.apellidos || !userData.fechaNacimiento || !userData.correo || !userData.nombreUsuario || !userData.contrasena) {
            this.showNotification('Por favor, complete todos los campos obligatorios', 'error');
            return;
        }

        // Validate age
        if (userData.edad < 13) {
            this.showNotification('El usuario debe tener al menos 13 años', 'error');
            return;
        }

        // Check if DNI already exists
        if (this.users.some(user => user.dni === userData.dni)) {
            this.showNotification('Ya existe un usuario con este DNI', 'error');
            return;
        }

        // Check if email already exists
        if (this.users.some(user => user.correo === userData.correo)) {
            this.showNotification('Ya existe un usuario con este correo', 'error');
            return;
        }

        // Check if username already exists
        if (this.users.some(user => user.nombreUsuario === userData.nombreUsuario)) {
            this.showNotification('Ya existe un usuario con este nombre de usuario', 'error');
            return;
        }

        // Add user (don't store password in plain text in production)
        this.users.push(userData);
        this.saveUsers();
        this.clearAllForms();
        this.showNotification('Usuario agregado exitosamente', 'success');
        
        // Switch to list tab
        this.switchTab('lista');
    }

    calculateAgeFromDate(fechaNacimiento) {
        if (!fechaNacimiento) return null;
        
        const birthDate = new Date(fechaNacimiento);
        const today = new Date();
        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        
        return age;
    }

    getFormData(formId) {
        const form = document.getElementById(formId);
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }

    handleSearch() {
        const searchData = {
            dni: document.getElementById('searchDni').value.toLowerCase(),
            nombre: document.getElementById('searchNombre').value.toLowerCase(),
            correo: document.getElementById('searchCorreo').value.toLowerCase(),
            usuario: document.getElementById('searchUsuario').value.toLowerCase(),
            edadMin: parseInt(document.getElementById('searchEdadMin').value) || null,
            edadMax: parseInt(document.getElementById('searchEdadMax').value) || null,
            estado: document.getElementById('searchEstado').value
        };

        const filteredUsers = this.users.filter(user => {
            const matchesDni = !searchData.dni || user.dni.toLowerCase().includes(searchData.dni);
            const matchesNombre = !searchData.nombre || 
                user.nombres.toLowerCase().includes(searchData.nombre) ||
                user.apellidos.toLowerCase().includes(searchData.nombre);
            const matchesCorreo = !searchData.correo || user.correo.toLowerCase().includes(searchData.correo);
            const matchesUsuario = !searchData.usuario || user.nombreUsuario.toLowerCase().includes(searchData.usuario);
            const matchesEdadMin = searchData.edadMin === null || user.edad >= searchData.edadMin;
            const matchesEdadMax = searchData.edadMax === null || user.edad <= searchData.edadMax;
            const matchesEstado = !searchData.estado || user.estado === searchData.estado;

            return matchesDni && matchesNombre && matchesCorreo && matchesUsuario && 
                   matchesEdadMin && matchesEdadMax && matchesEstado;
        });

        this.renderSearchResults(filteredUsers);
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
                <table class="user-table">
                    <thead>
                        <tr>
                            <th>DNI/Cédula</th>
                            <th>Nombre Completo</th>
                            <th>Edad</th>
                            <th>Correo</th>
                            <th>Usuario</th>
                            <th>Estado</th>
                            <th>Fecha Registro</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map(user => this.createUserRow(user)).join('')}
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
        document.getElementById('searchCorreo').value = '';
        document.getElementById('searchUsuario').value = '';
        document.getElementById('searchEdadMin').value = '';
        document.getElementById('searchEdadMax').value = '';
        document.getElementById('searchEstado').value = '';
        document.getElementById('searchResults').innerHTML = '';
    }

    renderUserList() {
        const tbody = document.getElementById('userTableBody');
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const paginatedUsers = this.users.slice(startIndex, endIndex);

        tbody.innerHTML = paginatedUsers.map(user => this.createUserRow(user)).join('');
        
        this.renderPagination();
        this.attachTableEventListeners();
    }

    createUserRow(user) {
        return `
            <tr>
                <td>${user.dni}</td>
                <td>${user.nombres} ${user.apellidos}</td>
                <td>
                    <span class="age-badge">
                        <i class="fas fa-birthday-cake"></i>
                        ${user.edad} años
                    </span>
                </td>
                <td>${user.correo}</td>
                <td>${user.nombreUsuario}</td>
                <td><span class="status-badge ${user.estado}">${user.estado}</span></td>
                <td>${user.fechaRegistro}</td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn edit" onclick="userManager.editUser(${user.id})" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-btn delete" onclick="userManager.deleteUser(${user.id})" title="Eliminar">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    renderPagination() {
        const pagination = document.getElementById('pagination');
        const totalPages = Math.ceil(this.users.length / this.itemsPerPage);
        
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        let paginationHTML = `
            <button class="pagination-btn" ${this.currentPage === 1 ? 'disabled' : ''} 
                    onclick="userManager.changePage(${this.currentPage - 1})">
                <i class="fas fa-chevron-left"></i>
            </button>
        `;

        for (let i = 1; i <= totalPages; i++) {
            paginationHTML += `
                <button class="pagination-btn ${i === this.currentPage ? 'active' : ''}" 
                        onclick="userManager.changePage(${i})">
                    ${i}
                </button>
            `;
        }

        paginationHTML += `
            <button class="pagination-btn" ${this.currentPage === totalPages ? 'disabled' : ''} 
                    onclick="userManager.changePage(${this.currentPage + 1})">
                <i class="fas fa-chevron-right"></i>
            </button>
        `;

        pagination.innerHTML = paginationHTML;
    }

    changePage(page) {
        const totalPages = Math.ceil(this.users.length / this.itemsPerPage);
        if (page >= 1 && page <= totalPages) {
            this.currentPage = page;
            this.renderUserList();
        }
    }

    attachTableEventListeners() {
        // Event listeners are attached via onclick in the HTML for simplicity
    }

    editUser(id) {
        const user = this.users.find(u => u.id === id);
        if (!user) return;

        const modal = document.getElementById('editModal');
        const modalBody = modal.querySelector('.modal-body');
        
        modalBody.innerHTML = `
            <form class="user-form" id="editUserForm">
                <input type="hidden" name="id" value="${user.id}">
                
                <div class="form-section">
                    <div class="form-header">
                        <h2><i class="fas fa-user"></i> Información personal</h2>
                    </div>
                    <div style="padding: 2rem;">
                        <div class="form-row">
                            <div class="form-group full-width">
                                <label for="editDni">DNI/CÉDULA *</label>
                                <input type="text" id="editDni" name="dni" value="${user.dni}" required>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="editNombres">Nombres *</label>
                                <input type="text" id="editNombres" name="nombres" value="${user.nombres}" required>
                            </div>
                            <div class="form-group">
                                <label for="editApellidos">Apellidos *</label>
                                <input type="text" id="editApellidos" name="apellidos" value="${user.apellidos}" required>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="editFechaNacimiento">Fecha de Nacimiento *</label>
                                <input type="date" id="editFechaNacimiento" name="fechaNacimiento" value="${user.fechaNacimiento}" required>
                            </div>
                            <div class="form-group">
                                <label for="editEdad">Edad</label>
                                <input type="number" id="editEdad" name="edad" value="${user.edad}" readonly>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="editTelefono">Teléfono</label>
                                <input type="tel" id="editTelefono" name="telefono" value="${user.telefono || ''}">
                            </div>
                            <div class="form-group">
                                <label for="editCorreo">Correo electrónico *</label>
                                <input type="email" id="editCorreo" name="correo" value="${user.correo}" required>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group full-width">
                                <label for="editDireccion">Dirección</label>
                                <input type="text" id="editDireccion" name="direccion" value="${user.direccion || ''}">
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="form-section">
                    <div class="form-header">
                        <h2><i class="fas fa-key"></i> Datos de la cuenta</h2>
                    </div>
                    <div style="padding: 2rem;">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="editNombreUsuario">Nombre de usuario *</label>
                                <input type="text" id="editNombreUsuario" name="nombreUsuario" value="${user.nombreUsuario}" required>
                            </div>
                            <div class="form-group">
                                <label for="editEstado">Estado *</label>
                                <select id="editEstado" name="estado" required>
                                    <option value="activo" ${user.estado === 'activo' ? 'selected' : ''}>Activo</option>
                                    <option value="inactivo" ${user.estado === 'inactivo' ? 'selected' : ''}>Inactivo</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-actions">
                            <button type="button" class="btn btn-secondary" onclick="userManager.closeModal()">
                                <i class="fas fa-times"></i>
                                Cancelar
                            </button>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i>
                                Actualizar
                            </button>
                        </div>
                    </div>
                </div>
            </form>
        `;

        // Add form submit listener
        const editForm = document.getElementById('editUserForm');
        editForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleEditUser(e);
        });

        // Add date change listener for age calculation in edit modal
        const editFechaNacimiento = document.getElementById('editFechaNacimiento');
        editFechaNacimiento.addEventListener('change', () => {
            const fechaNacimiento = editFechaNacimiento.value;
            const edadInput = document.getElementById('editEdad');
            
            if (fechaNacimiento) {
                const edad = this.calculateAgeFromDate(fechaNacimiento);
                edadInput.value = edad;
            }
        });

        modal.classList.add('active');
    }

    handleEditUser(e) {
        const formData = new FormData(e.target);
        const userId = parseInt(formData.get('id'));
        const userIndex = this.users.findIndex(u => u.id === userId);
        
        if (userIndex === -1) return;

        // Calculate age from birth date
        const edad = this.calculateAgeFromDate(formData.get('fechaNacimiento'));

        const updatedUser = {
            ...this.users[userIndex],
            dni: formData.get('dni'),
            nombres: formData.get('nombres'),
            apellidos: formData.get('apellidos'),
            fechaNacimiento: formData.get('fechaNacimiento'),
            edad: edad,
            telefono: formData.get('telefono'),
            correo: formData.get('correo'),
            direccion: formData.get('direccion'),
            nombreUsuario: formData.get('nombreUsuario'),
            estado: formData.get('estado')
        };

        // Validate required fields
        if (!updatedUser.dni || !updatedUser.nombres || !updatedUser.apellidos || !updatedUser.fechaNacimiento || !updatedUser.correo || !updatedUser.nombreUsuario) {
            this.showNotification('Por favor, complete todos los campos obligatorios', 'error');
            return;
        }

        // Validate age
        if (updatedUser.edad < 13) {
            this.showNotification('El usuario debe tener al menos 13 años', 'error');
            return;
        }

        // Check if DNI already exists (excluding current user)
        if (this.users.some(user => user.dni === updatedUser.dni && user.id !== userId)) {
            this.showNotification('Ya existe un usuario con este DNI', 'error');
            return;
        }

        // Check if email already exists (excluding current user)
        if (this.users.some(user => user.correo === updatedUser.correo && user.id !== userId)) {
            this.showNotification('Ya existe un usuario con este correo', 'error');
            return;
        }

        // Check if username already exists (excluding current user)
        if (this.users.some(user => user.nombreUsuario === updatedUser.nombreUsuario && user.id !== userId)) {
            this.showNotification('Ya existe un usuario con este nombre de usuario', 'error');
            return;
        }

        this.users[userIndex] = updatedUser;
        this.saveUsers();
        this.renderUserList();
        this.closeModal();
        this.showNotification('Usuario actualizado exitosamente', 'success');
    }

    deleteUser(id) {
        if (confirm('¿Está seguro de que desea eliminar este usuario?')) {
            this.users = this.users.filter(user => user.id !== id);
            this.saveUsers();
            this.renderUserList();
            this.showNotification('Usuario eliminado exitosamente', 'success');
        }
    }

    closeModal() {
        const modal = document.getElementById('editModal');
        modal.classList.remove('active');
    }

    clearAllForms() {
        const form1 = document.getElementById('nuevoUsuarioForm');
        const form2 = document.getElementById('datosUsuarioForm');
        if (form1) form1.reset();
        if (form2) form2.reset();
        
        // Clear calculated age
        const edadInput = document.getElementById('edad');
        if (edadInput) edadInput.value = '';
    }

    exportData() {
        const csvContent = this.generateCSV();
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `usuarios_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showNotification('Datos exportados exitosamente', 'success');
    }

    generateCSV() {
        const headers = ['DNI/Cédula', 'Nombres', 'Apellidos', 'Fecha Nacimiento', 'Edad', 'Correo', 'Teléfono', 'Dirección', 'Usuario', 'Estado', 'Fecha Registro'];
        const csvRows = [headers.join(',')];
        
        this.users.forEach(user => {
            const row = [
                user.dni,
                user.nombres,
                user.apellidos,
                user.fechaNacimiento || '',
                user.edad || '',
                user.correo,
                user.telefono || '',
                user.direccion || '',
                user.nombreUsuario,
                user.estado,
                user.fechaRegistro
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
        if (this.users.length === 0) {
            this.users = [
                {
                    id: 1,
                    dni: '12345678',
                    nombres: 'Ana María',
                    apellidos: 'García López',
                    fechaNacimiento: '1995-03-15',
                    edad: 29,
                    telefono: '+57 300 123 4567',
                    correo: 'ana.garcia@estudiante.com',
                    direccion: 'Calle 123 #45-67, Bogotá',
                    nombreUsuario: 'ana.garcia',
                    contrasena: 'password123', // En producción, esto debe estar encriptado
                    estado: 'activo',
                    fechaRegistro: '15/01/2024'
                },
                {
                    id: 2,
                    dni: '87654321',
                    nombres: 'Carlos Eduardo',
                    apellidos: 'Rodríguez Martínez',
                    fechaNacimiento: '1988-07-22',
                    edad: 36,
                    telefono: '+57 310 987 6543',
                    correo: 'carlos.rodriguez@estudiante.com',
                    direccion: 'Carrera 45 #12-34, Medellín',
                    nombreUsuario: 'carlos.rodriguez',
                    contrasena: 'password456',
                    estado: 'activo',
                    fechaRegistro: '20/01/2024'
                },
                {
                    id: 3,
                    dni: '11223344',
                    nombres: 'Laura Sofía',
                    apellidos: 'Hernández Pérez',
                    fechaNacimiento: '2001-11-08',
                    edad: 23,
                    telefono: '+57 320 456 7890',
                    correo: 'laura.hernandez@estudiante.com',
                    direccion: 'Avenida 80 #23-45, Cali',
                    nombreUsuario: 'laura.hernandez',
                    contrasena: 'password789',
                    estado: 'inactivo',
                    fechaRegistro: '25/01/2024'
                }
            ];
            this.saveUsers();
        }
    }

    loadUsers() {
        const stored = localStorage.getItem('sigma_users');
        return stored ? JSON.parse(stored) : [];
    }

    saveUsers() {
        localStorage.setItem('sigma_users', JSON.stringify(this.users));
    }
}

// Initialize the user manager when the page loads
let userManager;
document.addEventListener('DOMContentLoaded', () => {
    userManager = new UserManager();
});
