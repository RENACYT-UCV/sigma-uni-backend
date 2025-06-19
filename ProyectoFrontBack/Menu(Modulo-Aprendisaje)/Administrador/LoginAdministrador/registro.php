<?php
include 'login.php'; 

$nombre_completo = $_POST['nombre_completo']; 
$correo = $_POST['correo']; 
$usuario = $_POST['usuario']; 
$contrasena = $_POST['contrasena']; 
$query= "INSERT INTO Admi(nombrecompleto, correo, usuario, contrasena) VALUES('$nombre_completo', '$correo', '$usuario', '$contrasena')"; 
$ejecutar = mysqli_query($conn, $query); 

if($ejecutar){
    header("Location: login.html");
}else{
    echo '
     Inténtalo nuevamente
    '; 
}
?>