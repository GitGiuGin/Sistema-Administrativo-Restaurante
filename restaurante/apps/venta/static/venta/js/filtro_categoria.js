document.addEventListener("DOMContentLoaded", function () {
    const botones = document.querySelectorAll(".btn-categoria");
    const productos = document.querySelectorAll(".product-item");
    const buscador = document.getElementById("buscador-producto");
    let categoriaSeleccionada = "all";

    // --- FILTRO POR CATEGORIA ---
    botones.forEach(boton => {
        boton.addEventListener("click", function () {
            botones.forEach(b => b.classList.remove("active"));
            this.classList.add("active");
            categoriaSeleccionada = this.dataset.categoria;
            filtrarProductos();
        });
    });

    // --- FILTRO POR BUSCADOR ---
    buscador.addEventListener("input", function () {
        filtrarProductos();
    });

    // --- FUNCION CENTRAL DE FILTRADO ---
    function filtrarProductos() {
        const textoBusqueda = buscador.value.toLowerCase().trim();
        productos.forEach(producto => {
            const nombre = producto.dataset.nombre;
            const categoriaProducto = producto.dataset.categoria;
            const coincideCategoria =
                categoriaSeleccionada === "all" ||
                categoriaProducto === categoriaSeleccionada;
            const coincideBusqueda =
                nombre.includes(textoBusqueda);
            if (coincideCategoria && coincideBusqueda) {
                producto.style.display = "";
            } else {
                producto.style.display = "none";
            }
        });
    }
});
