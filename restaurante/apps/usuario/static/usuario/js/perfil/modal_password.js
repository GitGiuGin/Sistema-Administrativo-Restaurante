document.addEventListener("click", function (e) {
    if (e.target.closest(".btn-cambiar-password")) {
        const btn = e.target.closest(".btn-cambiar-password");
        const url = btn.getAttribute("data-url");

        fetch(url)
            .then(response => response.text())
            .then(html => {
                document.getElementById("contenidoModalCambiarPassword").innerHTML = html;
            });
    }
});