// Adicionar ao carrinho via AJAX (formulários nos cards de produto)
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.add-cart-form').forEach(function (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const url = form.action;
            const formData = new FormData(form);

            try {
                const res = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                    },
                    body: formData,
                });
                const data = await res.json();

                if (data.success) {
                    const badge = document.querySelector('.cart-badge');
                    if (badge) {
                        badge.textContent = data.total_itens;
                    } else {
                        const cartBtn = document.querySelector('.cart-btn');
                        if (cartBtn) {
                            const newBadge = document.createElement('span');
                            newBadge.className = 'cart-badge';
                            newBadge.textContent = data.total_itens;
                            cartBtn.appendChild(newBadge);
                        }
                    }

                    const btn = form.querySelector('.btn-add-cart');
                    if (btn) {
                        const original = btn.textContent;
                        btn.textContent = '✓ Adicionado!';
                        btn.style.background = '#059669';
                        setTimeout(() => {
                            btn.textContent = original;
                            btn.style.background = '';
                        }, 1500);
                    }
                }
            } catch (err) {
                console.error('Erro ao adicionar ao carrinho:', err);
                form.submit();
            }
        });
    });
});
