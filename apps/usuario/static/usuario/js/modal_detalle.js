document.addEventListener("click", function(e) {
    const btn = e.target.closest(".btn-detalle-usuario");
    if (!btn) return;

    e.preventDefault();

    const url = btn.getAttribute("data-url");
    const modalBody = document.getElementById("contenidoDetalleUsuario");

    modalBody.innerHTML = `
        <div class="text-center p-5">
            <div class="spinner-border"></div>
        </div>
    `;

    fetch(url)
        .then(response => response.text())
        .then(html => {
            modalBody.innerHTML = html;
        });
});