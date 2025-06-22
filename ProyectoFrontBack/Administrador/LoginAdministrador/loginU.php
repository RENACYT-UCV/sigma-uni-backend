<?php
include 'login.php'; 

$correo = $_POST['correo']; 
$contrasena = $_POST['contrasena']; 
$query= "SELECT * FROM Admi WHERE correo='$correo' AND contrasena= '$contrasena'"; 
$ejecutar = mysqli_query($conn, $query); 


if ($ejecutar->num_rows > 0) {
    // El usuario existe
    $_SESSION['correo'] = $correo;
    $_SESSION['contrasena'] = $contrasena;
    
    
        header("location: ../dashboardAdmin.html");
    
} else {
    // El usuario no existe
    echo "Correo o contraseña incorrecto.";
}

?>