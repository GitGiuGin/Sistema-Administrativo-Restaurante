document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("buscarProducto");

    input.addEventListener("keyup", function () {
        const query = this.value;

        const activeTab = document.querySelector(".tab-pane.active");
        const estado = activeTab.dataset.estado;

        fetch(`/productos/buscar/?q=${query}&estado=${estado}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById(`tabla-${estado}`).innerHTML = data.html;
            });
    });
});
