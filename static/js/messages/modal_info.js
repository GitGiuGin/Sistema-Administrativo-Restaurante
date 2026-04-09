document.addEventListener("DOMContentLoaded", function () {

    // 1️⃣ Cerrar modal de edición si existe
    const editModalEl = document.getElementById("editProductoModal");
    if (editModalEl) {
        const editModal = bootstrap.Modal.getInstance(editModalEl);
        if (editModal) {
            editModal.hide();
        }
    }

    // 2️⃣ Mostrar modal de información SOLO si existe
    const modalInfoEl = document.getElementById("modalInfo");
    if (modalInfoEl) {
        const infoModal = new bootstrap.Modal(modalInfoEl);
        infoModal.show();
    }
});