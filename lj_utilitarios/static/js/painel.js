// Auto-gerar slug a partir do nome
document.addEventListener('DOMContentLoaded', function () {
    const nomeEl = document.querySelector('input[name="nome"]');
    const slugEl = document.querySelector('input[name="slug"]');
    if (nomeEl && slugEl && !slugEl.value) {
        nomeEl.addEventListener('input', () => {
            slugEl.value = nomeEl.value
                .toLowerCase()
                .normalize('NFD').replace(/[̀-ͯ]/g, '')
                .replace(/[^a-z0-9\s-]/g, '')
                .trim().replace(/\s+/g, '-');
        });
    }
});
