<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: GET, POST, PUT, DELETE");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");

include_once '../database.php';

$database = new Database();
$db = $database->getConnection();

$method = $_SERVER['REQUEST_METHOD'];
$input = json_decode(file_get_contents('php://input'), true);

switch($method) {
    case 'GET':
        handleGet($db);
        break;
    case 'POST':
        handlePost($db, $input);
        break;
    case 'PUT':
        handlePut($db, $input);
        break;
    case 'DELETE':
        handleDelete($db);
        break;
    default:
        http_response_code(405);
        echo json_encode(['success' => false, 'message' => 'Método no permitido']);
        break;
}

function handleGet($db) {
    try {
        $page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
        $limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 10;
        $offset = ($page - 1) * $limit;
        
        // Búsqueda
        $search_conditions = [];
        $params = [];
        
        if (isset($_GET['dni']) && !empty($_GET['dni'])) {
            $search_conditions[] = "dni LIKE ?";
            $params[] = "%" . $_GET['dni'] . "%";
        }
        
        if (isset($_GET['nombre']) && !empty($_GET['nombre'])) {
            $search_conditions[] = "(nombres LIKE ? OR apellidos LIKE ?)";
            $params[] = "%" . $_GET['nombre'] . "%";
            $params[] = "%" . $_GET['nombre'] . "%";
        }
        
        if (isset($_GET['correo']) && !empty($_GET['correo'])) {
            $search_conditions[] = "correo LIKE ?";
            $params[] = "%" . $_GET['correo'] . "%";
        }
        
        if (isset($_GET['usuario']) && !empty($_GET['usuario'])) {
            $search_conditions[] = "nombre_usuario LIKE ?";
            $params[] = "%" . $_GET['usuario'] . "%";
        }
        
        if (isset($_GET['edad_min']) && !empty($_GET['edad_min'])) {
            $search_conditions[] = "edad >= ?";
            $params[] = $_GET['edad_min'];
        }
        
        if (isset($_GET['edad_max']) && !empty($_GET['edad_max'])) {
            $search_conditions[] = "edad <= ?";
            $params[] = $_GET['edad_max'];
        }
        
        if (isset($_GET['estado']) && !empty($_GET['estado'])) {
            $search_conditions[] = "estado = ?";
            $params[] = $_GET['estado'];
        }
        
        $where_clause = !empty($search_conditions) ? "WHERE " . implode(" AND ", $search_conditions) : "";
        
        // Contar total de registros
        $count_query = "SELECT COUNT(*) as total FROM usuarios $where_clause";
        $count_stmt = $db->prepare($count_query);
        $count_stmt->execute($params);
        $total_records = $count_stmt->fetch(PDO::FETCH_ASSOC)['total'];
        
        // Obtener registros paginados
        $query = "SELECT id, dni, nombres, apellidos, fecha_nacimiento, edad, telefono, correo, direccion, nombre_usuario, estado, fecha_registro 
                  FROM usuarios 
                  $where_clause 
                  ORDER BY fecha_registro DESC 
                  LIMIT $limit OFFSET $offset";
        
        $stmt = $db->prepare($query);
        $stmt->execute($params);
        $usuarios = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        $response = [
            'success' => true,
            'data' => $usuarios,
            'pagination' => [
                'current_page' => $page,
                'total_pages' => ceil($total_records / $limit),
                'total_records' => $total_records,
                'per_page' => $limit
            ]
        ];
        
        http_response_code(200);
        echo json_encode($response);
        
    } catch(Exception $e) {
        http_response_code(500);
        echo json_encode([
            'success' => false,
            'message' => 'Error al obtener usuarios: ' . $e->getMessage()
        ]);
    }
}

function handlePost($db, $input) {
    try {
        // Validar campos requeridos
        $required_fields = ['dni', 'nombres', 'apellidos', 'fecha_nacimiento', 'correo', 'nombre_usuario', 'contrasena'];
        foreach ($required_fields as $field) {
            if (!isset($input[$field]) || empty($input[$field])) {
                throw new Exception("El campo $field es requerido");
            }
        }
        
        // Calcular edad
        $fecha_nacimiento = new DateTime($input['fecha_nacimiento']);
        $hoy = new DateTime();
        $edad = $hoy->diff($fecha_nacimiento)->y;
        
        if ($edad < 13) {
            throw new Exception("El usuario debe tener al menos 13 años");
        }
        
        // Verificar duplicados
        $check_query = "SELECT COUNT(*) as count FROM usuarios WHERE dni = ? OR correo = ? OR nombre_usuario = ?";
        $check_stmt = $db->prepare($check_query);
        $check_stmt->execute([$input['dni'], $input['correo'], $input['nombre_usuario']]);
        $exists = $check_stmt->fetch(PDO::FETCH_ASSOC);
        
        if ($exists['count'] > 0) {
            throw new Exception("Ya existe un usuario con ese DNI, correo o nombre de usuario");
        }
        
        // Insertar usuario
        $query = "INSERT INTO usuarios (dni, nombres, apellidos, fecha_nacimiento, edad, telefono, correo, direccion, nombre_usuario, password, estado) 
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
        
        $stmt = $db->prepare($query);
        $hashed_password = password_hash($input['contrasena'], PASSWORD_DEFAULT);
        
        $stmt->execute([
            $input['dni'],
            $input['nombres'],
            $input['apellidos'],
            $input['fecha_nacimiento'],
            $edad,
            $input['telefono'] ?? null,
            $input['correo'],
            $input['direccion'] ?? null,
            $input['nombre_usuario'],
            $hashed_password,
            $input['estado'] ?? 'activo'
        ]);
        
        $user_id = $db->lastInsertId();
        
        http_response_code(201);
        echo json_encode([
            'success' => true,
            'message' => 'Usuario creado exitosamente',
            'data' => ['id' => $user_id]
        ]);
        
    } catch(Exception $e) {
        http_response_code(400);
        echo json_encode([
            'success' => false,
            'message' => $e->getMessage()
        ]);
    }
}

function handlePut($db, $input) {
    try {
        if (!isset($input['id']) || empty($input['id'])) {
            throw new Exception("ID de usuario requerido");
        }
        
        $user_id = $input['id'];
        
        // Verificar que el usuario existe
        $check_query = "SELECT id FROM usuarios WHERE id = ?";
        $check_stmt = $db->prepare($check_query);
        $check_stmt->execute([$user_id]);
        
        if (!$check_stmt->fetch()) {
            throw new Exception("Usuario no encontrado");
        }
        
        // Calcular edad si se proporciona fecha de nacimiento
        $edad = null;
        if (isset($input['fecha_nacimiento']) && !empty($input['fecha_nacimiento'])) {
            $fecha_nacimiento = new DateTime($input['fecha_nacimiento']);
            $hoy = new DateTime();
            $edad = $hoy->diff($fecha_nacimiento)->y;
            
            if ($edad < 13) {
                throw new Exception("El usuario debe tener al menos 13 años");
            }
        }
        
        // Verificar duplicados (excluyendo el usuario actual)
        $duplicates_check = [];
        $check_params = [];
        
        if (isset($input['dni'])) {
            $duplicates_check[] = "dni = ?";
            $check_params[] = $input['dni'];
        }
        if (isset($input['correo'])) {
            $duplicates_check[] = "correo = ?";
            $check_params[] = $input['correo'];
        }
        if (isset($input['nombre_usuario'])) {
            $duplicates_check[] = "nombre_usuario = ?";
            $check_params[] = $input['nombre_usuario'];
        }
        
        if (!empty($duplicates_check)) {
            $check_query = "SELECT COUNT(*) as count FROM usuarios WHERE (" . implode(" OR ", $duplicates_check) . ") AND id != ?";
            $check_params[] = $user_id;
            $check_stmt = $db->prepare($check_query);
            $check_stmt->execute($check_params);
            $exists = $check_stmt->fetch(PDO::FETCH_ASSOC);
            
            if ($exists['count'] > 0) {
                throw new Exception("Ya existe otro usuario con ese DNI, correo o nombre de usuario");
            }
        }
        
        // Construir query de actualización dinámicamente
        $update_fields = [];
        $params = [];
        
        $allowed_fields = ['dni', 'nombres', 'apellidos', 'fecha_nacimiento', 'telefono', 'correo', 'direccion', 'nombre_usuario', 'estado'];
        
        foreach ($allowed_fields as $field) {
            if (isset($input[$field])) {
                $update_fields[] = "$field = ?";
                $params[] = $input[$field];
            }
        }
        
        if ($edad !== null) {
            $update_fields[] = "edad = ?";
            $params[] = $edad;
        }
        
        if (empty($update_fields)) {
            throw new Exception("No hay campos para actualizar");
        }
        
        $params[] = $user_id;
        
        $query = "UPDATE usuarios SET " . implode(", ", $update_fields) . " WHERE id = ?";
        $stmt = $db->prepare($query);
        $stmt->execute($params);
        
        http_response_code(200);
        echo json_encode([
            'success' => true,
            'message' => 'Usuario actualizado exitosamente'
        ]);
        
    } catch(Exception $e) {
        http_response_code(400);
        echo json_encode([
            'success' => false,
            'message' => $e->getMessage()
        ]);
    }
}

function handleDelete($db) {
    try {
        if (!isset($_GET['id']) || empty($_GET['id'])) {
            throw new Exception("ID de usuario requerido");
        }
        
        $user_id = $_GET['id'];
        
        // Verificar que el usuario existe
        $check_query = "SELECT id FROM usuarios WHERE id = ?";
        $check_stmt = $db->prepare($check_query);
        $check_stmt->execute([$user_id]);
        
        if (!$check_stmt->fetch()) {
            throw new Exception("Usuario no encontrado");
        }
        
        // Eliminar usuario (esto también eliminará los puntajes por CASCADE)
        $query = "DELETE FROM usuarios WHERE id = ?";
        $stmt = $db->prepare($query);
        $stmt->execute([$user_id]);
        
        http_response_code(200);
        echo json_encode([
            'success' => true,
            'message' => 'Usuario eliminado exitosamente'
        ]);
        
    } catch(Exception $e) {
        http_response_code(400);
        echo json_encode([
            'success' => false,
            'message' => $e->getMessage()
        ]);
    }
}
?>
