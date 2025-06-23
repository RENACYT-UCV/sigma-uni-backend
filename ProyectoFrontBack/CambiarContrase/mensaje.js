document.querySelector('#changePasswordForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Previene el envío del formulario

    const formData = new FormData(event.target);

    fetch('CambioContr.php', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(text => {
        if (text.includes('Contraseña actualizada correctamente')) {
            const confirmationMessage = document.getElementById('confirmationMessage');
            confirmationMessage.classList.remove('hidden');

            // Redirigir después de 3 segundos
            setTimeout(() => {
                window.location.href = '../IngresarCorreo/correo.html';
            }, 3000);
        } else {
            alert(text); // Muestra otros posibles mensajes de error
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});