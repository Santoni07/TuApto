function checkSession() {
    fetch('/account/check_session/', { method: 'GET' })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.session_expired) {
                console.log("La sesión ha expirado. Redirigiendo a logout...");
                window.location.href = '/logout/'; // Redirigir al usuario
            } else {
                console.log("La sesión está activa.");
            }
        })
        .catch(error => {
            console.error('Error al verificar la sesión:', error.message);
            console.error('Detalles del error:', error);
        });
}
// Detectar clics en cualquier parte de la página
document.addEventListener('click', function() {
    checkSession();  // Comprobar sesión en cada clic
});