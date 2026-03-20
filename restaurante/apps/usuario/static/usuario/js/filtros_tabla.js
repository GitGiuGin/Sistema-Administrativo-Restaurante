const buscarInput = document.getElementById("buscarUsuario");
const filas = document.querySelectorAll("#userTable tr");
const tabActivos = document.getElementById("tabActivos");
const tabInactivos = document.getElementById("tabInactivos");

let estadoActual = tabActivos.classList.contains("active") ? "activo" : "inactivo";

function filtrarTabla() {
    let filtro = buscarInput.value.toLowerCase();

    filas.forEach(function (fila) {
        let estado = fila.getAttribute("data-estado");
        let texto = fila.innerText.toLowerCase();

        let coincideBusqueda = texto.includes(filtro);
        let coincideEstado = estado === estadoActual;

        fila.style.display = (coincideBusqueda && coincideEstado) ? "" : "none";
    });
}

tabActivos.addEventListener("click", function () {
    estadoActual = "activo";
    tabActivos.classList.add("active");
    tabInactivos.classList.remove("active");
    filtrarTabla();
});

tabInactivos.addEventListener("click", function () {
    estadoActual = "inactivo";
    tabInactivos.classList.add("active");
    tabActivos.classList.remove("active");
    filtrarTabla();
});

buscarInput.addEventListener("keyup", filtrarTabla);

filtrarTabla();