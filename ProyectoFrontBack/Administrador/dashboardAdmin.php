<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: GET");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");

include_once '../database.php';

$database = new Database();
$db = $database->getConnection();

$method = $_SERVER['REQUEST_METHOD'];

if ($method == 'GET') {
    try {
        // Estadísticas generales
        $stats = [];
        
        // Total de usuarios
        $query = "SELECT COUNT(*) as total FROM usuarios WHERE estado = 'activo'";
        $stmt = $db->prepare($query);
        $stmt->execute();
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        $stats['usuarios_totales'] = $result['total'];
        
        // Usuarios nuevos este mes
        $query = "SELECT COUNT(*) as total FROM usuarios WHERE MONTH(fecha_registro) = MONTH(CURRENT_DATE()) AND YEAR(fecha_registro) = YEAR(CURRENT_DATE())";
        $stmt = $db->prepare($query);
        $stmt->execute();
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        $stats['usuarios_nuevos_mes'] = $result['total'];
        
        // Datos para gráfico de puntajes (últimos 7 días)
        $query = "SELECT 
                    DATE(fecha_puntaje) as fecha,
                    AVG(puntaje) as puntaje_promedio,
                    DAYNAME(fecha_puntaje) as dia_semana
                  FROM puntajes 
                  WHERE fecha_puntaje >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
                  GROUP BY DATE(fecha_puntaje), DAYNAME(fecha_puntaje)
                  ORDER BY fecha_puntaje";
        $stmt = $db->prepare($query);
        $stmt->execute();
        $puntajes_semana = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        // Datos para gráfico de usuarios por mes (último año)
        $query = "SELECT 
                    MONTH(fecha_registro) as mes,
                    YEAR(fecha_registro) as año,
                    COUNT(*) as total_usuarios,
                    MONTHNAME(fecha_registro) as nombre_mes
                  FROM usuarios 
                  WHERE fecha_registro >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
                  GROUP BY YEAR(fecha_registro), MONTH(fecha_registro)
                  ORDER BY año, mes";
        $stmt = $db->prepare($query);
        $stmt->execute();
        $usuarios_por_mes = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        // Actividad reciente
        $query = "SELECT 
                    u.nombres, u.apellidos, p.puntaje, p.fecha_puntaje
                  FROM puntajes p
                  JOIN usuarios u ON p.usuario_id = u.id
                  ORDER BY p.fecha_puntaje DESC
                  LIMIT 10";
        $stmt = $db->prepare($query);
        $stmt->execute();
        $actividad_reciente = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        $response = [
            'success' => true,
            'data' => [
                'estadisticas' => $stats,
                'puntajes_semana' => $puntajes_semana,
                'usuarios_por_mes' => $usuarios_por_mes,
                'actividad_reciente' => $actividad_reciente
            ]
        ];
        
        http_response_code(200);
        echo json_encode($response);
        
    } catch(Exception $e) {
        http_response_code(500);
        echo json_encode([
            'success' => false,
            'message' => 'Error al obtener datos del dashboard: ' . $e->getMessage()
        ]);
    }
} else {
    http_response_code(405);
    echo json_encode([
        'success' => false,
        'message' => 'Método no permitido'
    ]);
}
?>
