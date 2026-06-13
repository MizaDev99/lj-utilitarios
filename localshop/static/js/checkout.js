/* ============================================================
   Checkout JS — L&J Utilitários
   Comportamento dinâmico: recebimento, frete, pagamento
   ============================================================ */

let freteAtual = 0;

// ── Forma de Recebimento ──────────────────────────────────

function handleRecebimento(valor) {
    const entregaFields = document.getElementById('entrega-fields');
    const retiradaInfo  = document.getElementById('retirada-info');
    const optEntrega    = document.getElementById('opt-entrega');
    const optRetirada   = document.getElementById('opt-retirada');

    if (valor === 'retirada') {
        entregaFields.style.display  = 'none';
        retiradaInfo.style.display   = 'block';
        optEntrega.classList.remove('ativo');
        optRetirada.classList.add('ativo');
        atualizarFrete(0, true);
    } else {
        entregaFields.style.display  = 'block';
        retiradaInfo.style.display   = 'none';
        optEntrega.classList.add('ativo');
        optRetirada.classList.remove('ativo');
        // re-busca frete da cidade selecionada (se tiver)
        const cidadeSelect = document.getElementById('id_cidade_select');
        if (cidadeSelect && cidadeSelect.value) {
            buscarFrete(cidadeSelect.value);
        } else {
            atualizarFrete(0, false);
        }
    }
}

// ── Cálculo de frete por cidade ───────────────────────────

document.addEventListener('DOMContentLoaded', function () {
    const cidadeSelect = document.getElementById('id_cidade_select');
    if (cidadeSelect) {
        cidadeSelect.addEventListener('change', function () {
            const cidade = this.value;
            if (cidade) {
                buscarFrete(cidade);
            } else {
                atualizarFrete(0, false);
            }
        });
    }
});

async function buscarFrete(cidade) {
    try {
        const res = await fetch(`${FRETE_URL}?cidade=${encodeURIComponent(cidade)}`);
        const data = await res.json();
        const frete = parseFloat(data.frete);
        atualizarFrete(frete, false);
    } catch (err) {
        console.error('Erro ao buscar frete:', err);
    }
}

function atualizarFrete(frete, isRetirada) {
    freteAtual = frete;
    const freteEl = document.getElementById('resumo-frete-display');
    const totalEl = document.getElementById('resumo-total-display');

    if (isRetirada) {
        freteEl.innerHTML = '<strong style="color:var(--cor-sucesso);">Grátis ✅ (retirada)</strong>';
    } else if (frete === 0) {
        freteEl.innerHTML = '<em style="color:var(--cor-texto-suave); font-size:13px;">selecione a cidade</em>';
    } else {
        freteEl.innerHTML = `<span>R$ ${frete.toFixed(2)}</span>`;
    }

    const total = SUBTOTAL + freteAtual;
    totalEl.textContent = `R$ ${total.toFixed(2)}`;

    // anima o total
    totalEl.classList.remove('total-anim');
    void totalEl.offsetWidth;
    totalEl.classList.add('total-anim');
}

// ── Forma de Pagamento ────────────────────────────────────

function handlePagamento(valor) {
    const cartaoInfo = document.getElementById('cartao-info');
    const pixInfo    = document.getElementById('pix-info');
    const trocoField = document.getElementById('troco-field');

    // ocultar tudo primeiro
    [cartaoInfo, pixInfo, trocoField].forEach(el => {
        if (el) { el.style.display = 'none'; }
    });

    // marcar botão ativo
    document.querySelectorAll('#pagamento-group .radio-opt').forEach(opt => {
        opt.classList.remove('ativo');
    });
    const radioChecked = document.querySelector(`input[name="forma_pagamento"][value="${valor}"]`);
    if (radioChecked) radioChecked.closest('.radio-opt').classList.add('ativo');

    if (valor === 'pix') {
        if (pixInfo) pixInfo.style.display = 'block';
    } else if (valor === 'dinheiro') {
        if (trocoField) trocoField.style.display = 'block';
        if (cartaoInfo) {
            cartaoInfo.style.display = 'block';
            cartaoInfo.innerHTML = '💵 Pagamento em dinheiro na entrega ou na retirada.';
        }
    } else {
        if (cartaoInfo) {
            cartaoInfo.style.display = 'block';
            cartaoInfo.innerHTML = '💳 Pagamento realizado na entrega ou na retirada.';
        }
    }
}

// ── Copiar chave Pix ──────────────────────────────────────

function copiarPix() {
    const chaveEl = document.getElementById('pix-chave-txt');
    if (!chaveEl) return;
    const texto = chaveEl.textContent.trim();
    navigator.clipboard.writeText(texto).then(() => {
        const btn = document.querySelector('.btn-copiar-pix');
        if (btn) {
            btn.textContent = '✅ Copiado!';
            setTimeout(() => { btn.textContent = '📋 Copiar chave'; }, 2000);
        }
    }).catch(() => {
        const range = document.createRange();
        range.selectNodeContents(chaveEl);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
    });
}

// ── Init ──────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function () {
    // Marcar opção ativa inicial de recebimento
    const recebimento = document.querySelector('input[name="forma_recebimento"]:checked');
    if (recebimento) {
        recebimento.closest('.radio-opt')?.classList.add('ativo');
    }
    // Marcar opção ativa inicial de pagamento
    const pagamento = document.querySelector('input[name="forma_pagamento"]:checked');
    if (pagamento) {
        pagamento.closest('.radio-opt')?.classList.add('ativo');
    }
});

// Expor globalmente (usados pelos onchange inline no HTML)
window.handleRecebimento = handleRecebimento;
window.handlePagamento   = handlePagamento;
window.copiarPix         = copiarPix;
