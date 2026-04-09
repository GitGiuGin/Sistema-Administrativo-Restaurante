document.addEventListener("DOMContentLoaded", () => {
    const editModal = document.getElementById("editProductoModal");

    editModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;

        const id = button.getAttribute("data-producto");
        const nombre = button.getAttribute("data-nombre");
        const categoria = button.getAttribute("data-categoria");
        const costoStr = button.getAttribute("data-preciocosto").replace(",", ".");
        const ventaStr = button.getAttribute("data-precioventa").replace(",", ".");
        const costo = parseFloat(costoStr);
        const venta = parseFloat(ventaStr);

        document.getElementById("productoId").value = id;
        document.getElementById("nombre").value = nombre;
        document.getElementById("categoria").value = categoria;
        document.getElementById("precio_costo").value = costo;
        document.getElementById("precio_venta").value = venta;

        // Set action
        document.getElementById("formEditarProducto").action = `/productos/editar/${id}/`;
    });
});