document.addEventListener("submit", function(e) {
    const form = e.target;

    if (form.id === "formCambiarPassword") {
        e.preventDefault();

        const formData = new FormData(form);

        fetch(form.action, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": form.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(res => res.text())
        .then(html => {
            document.getElementById("contenidoModalCambiarPassword").innerHTML = html;
        });
    }
});