document.addEventListener("DOMContentLoaded", function () {
    var modal = document.getElementById('confirmInhabilitarModal');

    modal.addEventListener('show.bs.modal', event => {
        const button = event.relatedTarget; // botón que abrió el modal
        const productoId = button.getAttribute('data-producto');
        const productoNombre = button.getAttribute('data-nombre');

        // Actualizar nombre del producto en el modal
        const nombreElemento = modal.querySelector('#nombreProducto');
        nombreElemento.textContent = productoNombre;

        // Cambiar action del formulario
        const form = modal.querySelector('#formInhabilitar');
        form.action = `/productos/inhabilitar/${productoId}/`;
    });
});