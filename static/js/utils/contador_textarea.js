document.addEventListener("DOMContentLoaded", function () {

    function activarContador(textareaId, contadorId) {
        const textarea = document.getElementById(textareaId);
        const contador = document.getElementById(contadorId);

        if (!textarea || !contador) return;

        textarea.addEventListener("input", function () {
            const len = this.value.length;
            const max = this.maxLength;

            contador.textContent = `${len} / ${max}`;
            contador.classList.toggle("text-danger", len >= max);
        });
    }

    // activar para tu campo
    activarContador("descripcionAdmin", "contadorDescripcionAdmin");

});