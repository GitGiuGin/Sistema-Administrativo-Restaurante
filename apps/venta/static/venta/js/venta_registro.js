document.getElementById("form-registrar-venta")
    .addEventListener("submit", function () {

        const carritoInput = document.getElementById("carrito-data-input");

        if (!window.carrito || window.carrito.length === 0) {
            return;
        }

        carritoInput.value = JSON.stringify(window.carrito);
    });