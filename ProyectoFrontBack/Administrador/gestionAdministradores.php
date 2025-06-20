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
        
        if (isset($_GET['email']) && !empty($_GET['email'])) {
            $search_conditions[] = "email LIKE ?";
            $params[] = "%" . $_GET['email'] . "%";
        }
        
        if (isset($_GET['rol']) && !empty($_GET['rol'])) {
            $search_conditions[] = "rol = ?";
            $params[] = $_GET['rol'];
        }
        
        if (isset($_GET['estado']) && !empty($_GET['estado'])) {
            $search_conditions[] = "estado = ?";
            $params[] = $_GET['estado'];
        }
        
        $where_clause = !empty($search_conditions) ? "WHERE " . implode(" AND ", $search_conditions) : "";
        
        // Contar total de registros
        $count_query = "SELECT COUNT(*) as total FROM administradores $where_clause";
        $count_stmt = $db->prepare($count_query);
        $count_stmt->execute($params);
        $total_records = $count_stmt->fetch(PDO::FETCH_ASSOC)['total'];
        
        // Obtener registros paginados
        $query = "SELECT id, dni, nombres, apellidos, telefono, email, direccion, rol, estado, fecha_registro 
                  FROM administradores 
                  $where_clause 
                  ORDER BY fecha_registro DESC 
                  LIMIT $limit OFFSET $offset";
        
        $stmt = $db->prepare($query);
        $stmt->execute($params);
        $administradores = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        $response = [
            'success' => true,
            'data' => $administradores,
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
            'message' => 'Error al obtener administradores: ' . $e->getMessage()
        ]);
    }
}

function handlePost($db, $input) {
    try {
        // Validar campos requeridos
        $required_fields = ['dni', 'nombres', 'apellidos', 'email', 'rol'];
        foreach ($required_fields as $field) {
            if (!isset($input[$field]) || empty($input[$field])) {
                throw new Exception("El campo $field es requerido");
            }
        }
        
        // Validar email
        if (!filter_var($input['email'], FILTER_VALIDATE_EMAIL)) {
            throw new Exception("Email no válido");
        }
        
        // Verificar duplicados
        $check_query = "SELECT COUNT(*) as count FROM administradores WHERE dni = ? OR email = ?";
        $check_stmt = $db->prepare($check_query);
        $check_stmt->execute([$input['dni'], $input['email']]);
        $exists = $check_stmt->fetch(PDO::FETCH_ASSOC);
        
        if ($exists['count'] > 0) {
            throw new Exception("Ya existe un administrador con ese DNI o email");
        }
        
        // Generar contraseña temporal
        $temp_password = 'admin' . rand(1000, 9999);
        $hashed_password = password_hash($temp_password, PASSWORD_DEFAULT);
        
        // Insertar administrador
        $query = "INSERT INTO administradores (dni, nombres, apellidos, telefono, email, direccion, rol, estado, password) 
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)";
        
        $stmt = $db->prepare($query);
        $stmt->execute([
            $input['dni'],
            $input['nombres'],
            $input['apellidos'],
            $input['telefono'] ?? null,
            $input['email'],
            $input['direccion'] ?? null,
            $input['rol'],
            $input['estado'] ?? 'activo',
            $hashed_password
        ]);
        
        $admin_id = $db->lastInsertId();
        
        http_response_code(201);
        echo json_encode([
            'success' => true,
            'message' => 'Administrador creado exitosamente',
            'data' => [
                'id' => $admin_id,
                'temp_password' => $temp_password
            ]
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
            throw new Exception("ID de administrador requerido");
        }
        
        $admin_id = $input['id'];
        
        // Verificar que el administrador existe
        $check_query = "SELECT id FROM administradores WHERE id = ?";
        $check_stmt = $db->prepare($check_query);
        $check_stmt->execute([$admin_id]);
        
        if (!$check_stmt->fetch()) {
            throw new Exception("Administrador no encontrado");
        }
        
        // Validar email si se proporciona
        if (isset($input['email']) && !filter_var($input['email'], FILTER_VALIDATE_EMAIL)) {
            throw new Exception("Email no válido");
        }
        
        // Verificar duplicados (excluyendo el administrador actual)
        $duplicates_check = [];
        $check_params = [];
        
        if (isset($input['dni'])) {
            $duplicates_check[] = "dni = ?";
            $check_params[] = $input['dni'];
        }
        if (isset($input['email'])) {
            $duplicates_check[] = "email = ?";
            $check_params[] = $input['email'];
        }
        
        if (!empty($duplicates_check)) {
            $check_query = "SELECT COUNT(*) as count FROM administradores WHERE (" . implode(" OR ", $duplicates_check) . ") AND id != ?";
            $check_params[] = $admin_id;
            $check_stmt = $db->prepare($check_query);
            $check_stmt->execute($check_params);
            $exists = $check_stmt->fetch(PDO::FETCH_ASSOC);
            
            if ($exists['count'] > 0) {
                throw new Exception("Ya existe otro administrador con ese DNI o email");
            }
        }
        
        // Construir query de actualización dinámicamente
        $update_fields = [];
        $params = [];
        
        $allowed_fields = ['dni', 'nombres', 'apellidos', 'telefono', 'email', 'direccion', 'rol', 'estado'];
        
        foreach ($allowed_fields as $field) {
            if (isset($input[$field])) {
                $update_fields[] = "$field = ?";
                $params[] = $input[$field];
            }
        }
        
        if (empty($update_fields)) {
            throw new Exception("No hay campos para actualizar");
        }
        
        $params[] = $admin_id;
        
        $query = "UPDATE administradores SET " . implode(", ", $update_fields) . " WHERE id = ?";
        $stmt = $db->prepare($query);
        $stmt->execute($params);
        
        http_response_code(200);
        echo json_encode([
            'success' => true,
            'message' => 'Administrador actualizado exitosamente'
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
            throw new Exception("ID de administrador requerido");
        }
        
        $admin_id = $_GET['id'];
        
        // Verificar que el administrador existe
        $check_query = "SELECT id, rol FROM administradores WHERE id = ?";
        $check_stmt = $db->prepare($check_query);
        $check_stmt->execute([$admin_id]);
        $admin = $check_stmt->fetch(PDO::FETCH_ASSOC);
        
        if (!$admin) {
            throw new Exception("Administrador no encontrado");
        }
        
        // Verificar que no sea el último super_admin
        if ($admin['rol'] === 'super_admin') {
            $count_query = "SELECT COUNT(*) as count FROM administradores WHERE rol = 'super_admin' AND estado = 'activo'";
            $count_stmt = $db->prepare($count_query);
            $count_stmt->execute();
            $super_admin_count = $count_stmt->fetch(PDO::FETCH_ASSOC)['count'];
            
            if ($super_admin_count <= 1) {
                throw new Exception("No se puede eliminar el último super administrador activo");
            }
        }
        
        // Eliminar administrador
        $query = "DELETE FROM administradores WHERE id = ?";
        $stmt = $db->prepare($query);
        $stmt->execute([$admin_id]);
        
        http_response_code(200);
        echo json_encode([
            'success' => true,
            'message' => 'Administrador eliminado exitosamente'
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
