document.addEventListener("DOMContentLoaded", function () {

    // ==============================
    // REFERENCIAS DOM
    // ==============================

    const carritoBody = document.querySelector(".table-body-scroll");
    const carritoTotal = document.querySelector(".card-footer h5");
    const carritoCount = document.querySelector(".badge");

    const montoRecibidoInput = document.getElementById("monto-recibido");
    const montoVueltoInput = document.getElementById("monto-vuelto");

    const productos = document.querySelectorAll(".product-clickable");

    // ==============================
    // ESTADO DEL CARRITO
    // ==============================

    window.carrito = [];

    // ==============================
    // AGREGAR PRODUCTO AL HACER CLICK
    // ==============================

    productos.forEach(producto => {

        producto.addEventListener("click", function () {

            const id = producto.dataset.id;
            const nombre = producto.dataset.nombre;
            const precio = parseFloat(producto.dataset.precio);

            agregarAlCarrito(id, nombre, precio);
        });

    });

    // ==============================
    // FUNCION AGREGAR
    // ==============================

    function agregarAlCarrito(id, nombre, precio) {

        const productoExistente = window.carrito.find(p => p.id === id);

        if (productoExistente) {
            productoExistente.cantidad += 1;
        } else {
            window.carrito.push({
                id: id,
                nombre: nombre,
                precio: precio,
                cantidad: 1
            });
        }

        renderCarrito();
    }

    // ==============================
    // RENDERIZAR CARRITO
    // ==============================

    function renderCarrito() {

        carritoBody.innerHTML = "";

        if (window.carrito.length === 0) {
            carritoBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted">
                        No hay productos en el carrito
                    </td>
                </tr>
            `;
        }

        let total = 0;
        let totalItems = 0;

        window.carrito.forEach((producto, index) => {

            const subtotal = producto.precio * producto.cantidad;
            total += subtotal;
            totalItems += producto.cantidad;

            const fila = document.createElement("tr");

            fila.innerHTML = `
                <td style="width: 40%;">${producto.nombre}</td>
                <td style="width: 15%;" class="text-center">${producto.precio.toFixed(2)}</td>
                <td style="width: 15%;" class="text-center">
                    <input type="number"
                            class="form-control form-control-sm cantidad-input"
                            value="${producto.cantidad}"
                            min="1"
                            data-index="${index}">
                </td>
                <td style="width: 15%;" class="text-center">${subtotal.toFixed(2)}</td>
                <td style="width: 15%;" class="text-end">
                    <button class="btn btn-sm btn-outline-danger eliminar-btn"
                            data-index="${index}">
                        ✕
                    </button>
                </td>
            `;

            carritoBody.appendChild(fila);
        });

        carritoTotal.textContent = `Bs. ${total.toFixed(2)}`;
        carritoCount.textContent = `${totalItems} ítems`;

        calcularVuelto(total);

        activarEventosInputs();
    }

    // ==============================
    // ACTUALIZAR CANTIDAD Y ELIMINAR
    // ==============================

    function activarEventosInputs() {

        const cantidadInputs = document.querySelectorAll(".cantidad-input");
        const eliminarBtns = document.querySelectorAll(".eliminar-btn");

        cantidadInputs.forEach(input => {
            input.addEventListener("input", function () {

                const index = this.dataset.index;
                const nuevaCantidad = parseInt(this.value);

                if (nuevaCantidad > 0) {
                    window.carrito[index].cantidad = nuevaCantidad;
                }

                renderCarrito();
            });
        });

        eliminarBtns.forEach(btn => {
            btn.addEventListener("click", function () {

                const index = this.dataset.index;
                window.carrito.splice(index, 1);

                renderCarrito();
            });
        });
    }

    // ==============================
    // CALCULAR VUELTO
    // ==============================

    function calcularVuelto(total) {

        const montoRecibido = parseFloat(montoRecibidoInput.value) || 0;
        const vuelto = montoRecibido - total;

        if (vuelto < 0) {
            montoVueltoInput.value = `Falta: Bs. ${Math.abs(vuelto).toFixed(2)}`;
            montoVueltoInput.classList.add("text-danger");
            montoVueltoInput.classList.remove("text-success");
        } else {
            montoVueltoInput.value = `Bs. ${vuelto.toFixed(2)}`;
            montoVueltoInput.classList.add("text-success");
            montoVueltoInput.classList.remove("text-danger");
        }
    }

    // ==============================
    // EVENTO MONTO RECIBIDO
    // ==============================

    montoRecibidoInput.addEventListener("input", function () {

        const totalTexto = carritoTotal.textContent.replace("Bs. ", "");
        const total = parseFloat(totalTexto) || 0;

        calcularVuelto(total);
    });

});
