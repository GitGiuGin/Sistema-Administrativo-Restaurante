document.addEventListener('DOMContentLoaded', () => {
    const select = document.getElementById('categoriaSelect');

    select.addEventListener('change', () => {
        if (select.value === 'nueva_categoria') {
            window.location.href = select.dataset.url;
        }
    });
});