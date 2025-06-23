-- Crear base de datos
CREATE DATABASE IF NOT EXISTS sigma_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE sigma_db;

-- Tabla de usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dni VARCHAR(20) UNIQUE,
    nombres VARCHAR(100),
    apellidos VARCHAR(100),
    fecha_nacimiento DATE,
    telefono VARCHAR(20),
    correo VARCHAR(100) UNIQUE NOT NULL,
    direccion VARCHAR(255),
    usuario VARCHAR(50) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol ENUM('usuario', 'admin') DEFAULT 'usuario',
    estado ENUM('activo', 'inactivo') DEFAULT 'activo',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla fija de lecciones
CREATE TABLE lecciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL -- Ej: 'números', 'letras', 'comidas', 'preguntas'
);

-- Insertar las 4 lecciones fijas
INSERT INTO lecciones (nombre) VALUES
('números'),
('letras'),
('comidas'),
('preguntas');

-- Registro de lecciones completadas por usuario
CREATE TABLE lecciones_usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    leccion_id INT NOT NULL,
    completado BOOLEAN DEFAULT TRUE,
    fecha_completado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (leccion_id) REFERENCES lecciones(id) ON DELETE CASCADE,
    UNIQUE (usuario_id, leccion_id) -- Evita duplicados
);

-- Tabla de comentarios enviados por los usuarios
CREATE TABLE comentarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    comentario TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);