// AJAX para adicionar ao carrinho nos cards de produto
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.add-cart-form').forEach(form => {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const fd = new FormData(form);
            try {
                const res = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': fd.get('csrfmiddlewaretoken'),
                    },
                    body: fd,
                });
                const data = await res.json();
                if (data.success) {
                    const badge = document.getElementById('cart-badge');
                    if (badge) {
                        badge.textContent = data.total_itens;
                        badge.style.display = data.total_itens > 0 ? '' : 'none';
                    }
                    const btn = form.querySelector('.btn-add-cart');
                    if (btn) {
                        const orig = btn.textContent;
                        btn.textContent = '✓ Adicionado!';
                        btn.style.background = 'linear-gradient(90deg, #059669, #00C48C)';
                        setTimeout(() => {
                            btn.textContent = orig;
                            btn.style.background = '';
                        }, 1500);
                    }
                }
            } catch (err) {
                form.submit();
            }
        });
    });
});
