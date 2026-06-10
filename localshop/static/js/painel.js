// Auto-gerar slug a partir do nome no formulário de produto/categoria
document.addEventListener('DOMContentLoaded', function () {
    const nomeInput = document.querySelector('input[name="nome"]');
    const slugInput = document.querySelector('input[name="slug"]');

    if (nomeInput && slugInput && !slugInput.value) {
        nomeInput.addEventListener('input', function () {
            slugInput.value = nomeInput.value
                .toLowerCase()
                .normalize('NFD').replace(/[̀-ͯ]/g, '')
                .replace(/[^a-z0-9\s-]/g, '')
                .trim()
                .replace(/\s+/g, '-');
        });
    }

    // Confirmar exclusão
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            if (!confirm(el.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });
});
