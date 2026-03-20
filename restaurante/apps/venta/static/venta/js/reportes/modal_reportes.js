document.addEventListener("DOMContentLoaded", function () {

    const modalElement = document.getElementById("modalDetalleDia");
    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    const contenedor = document.getElementById("contenidoDetalleDia");

    document.addEventListener("click", function (e) {

        const btn = e.target.closest(".btn-detalle-dia");
        if (!btn) return;

        const fecha = btn.dataset.fecha;
        const mes   = btn.dataset.mes;

        let url = "/ventas/detalle-productos/?";

        if (fecha) {
            url += `fecha=${fecha}`;
        } else if (mes) {
            url += `mes=${mes}`;
        } else {
            console.error("No se pasó ni fecha ni mes");
            return;
        }

        modal.show();

        contenedor.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border text-primary"></div>
            </div>
        `;

        fetch(url)
            .then(response => response.text())
            .then(html => {
                contenedor.innerHTML = html;
            });

    });

});