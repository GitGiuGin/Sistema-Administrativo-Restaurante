document.querySelectorAll(".toggle-ver-ventas").forEach(checkbox => {
    checkbox.addEventListener("change", function () {
        const categoriaId = this.dataset.categoriaId;
        fetch(TOGGLE_VER_VENTAS_URL, {
            method: "POST",
            headers: {
                "X-CSRFToken": CSRF_TOKEN,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `categoria_id=${categoriaId}`
        })
            .then(res => res.json())
            .then(data => {
                if (!data.ok) {
                    alert(data.error || "Error al actualizar");
                    this.checked = !this.checked; // rollback
                } else {
                    // actualizar tooltip
                    this.title = this.checked
                        ? "Quitar esta categoría del catálogo de ventas"
                        : "Mostrar esta categoría en el catálogo de ventas";
                }
            })
            .catch(() => {
                alert("Error de conexión");
                this.checked = !this.checked;
            });
    });
});