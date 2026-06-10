from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from produtos.models import Produto, Categoria, ImagemProduto
from produtos.forms import ProdutoForm, CategoriaForm
from pedidos.models import Pedido
from core.models import Configuracao
from .forms import ConfiguracaoForm, StatusPedidoForm


def staff_required(view_func):
    return user_passes_test(
        lambda u: u.is_active and (u.is_staff or u.is_superuser),
        login_url='/painel/login/'
    )(view_func)


def painel_login(request):
    if request.user.is_authenticated:
        return redirect('painel:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect('painel:dashboard')
        messages.error(request, 'Credenciais inválidas ou sem permissão de acesso.')

    return render(request, 'painel/login.html')


@login_required(login_url='/painel/login/')
def painel_logout(request):
    logout(request)
    return redirect('painel:login')


@staff_required
def dashboard(request):
    hoje = timezone.now().date()
    primeiro_dia_mes = hoje.replace(day=1)

    pedidos_hoje = Pedido.objects.filter(criado_em__date=hoje).count()
    pedidos_pendentes = Pedido.objects.filter(status='aguardando').count()

    fat_mes_qs = Pedido.objects.filter(
        criado_em__date__gte=primeiro_dia_mes,
        status__in=['confirmado', 'enviado', 'entregue']
    ).aggregate(total=Sum('total'))
    faturamento_mes = fat_mes_qs['total'] or 0

    produtos_ativos = Produto.objects.filter(ativo=True).count()
    pedidos_recentes = Pedido.objects.all()[:10]

    context = {
        'pedidos_hoje': pedidos_hoje,
        'pedidos_pendentes': pedidos_pendentes,
        'faturamento_mes': faturamento_mes,
        'produtos_ativos': produtos_ativos,
        'pedidos_recentes': pedidos_recentes,
    }
    return render(request, 'painel/dashboard.html', context)


@staff_required
def produtos_lista(request):
    busca = request.GET.get('q', '')
    produtos = Produto.objects.select_related('categoria').all()
    if busca:
        produtos = produtos.filter(Q(nome__icontains=busca) | Q(categoria__nome__icontains=busca))
    return render(request, 'painel/produtos_lista.html', {'produtos': produtos, 'busca': busca})


@staff_required
def produto_criar(request):
    form = ProdutoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        produto = form.save()
        messages.success(request, f'Produto "{produto.nome}" criado com sucesso!')
        return redirect('painel:produtos')
    return render(request, 'painel/produto_form.html', {'form': form, 'titulo': 'Novo Produto'})


@staff_required
def produto_editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    form = ProdutoForm(request.POST or None, request.FILES or None, instance=produto)
    if form.is_valid():
        produto = form.save()
        messages.success(request, f'Produto "{produto.nome}" atualizado!')
        return redirect('painel:produtos')
    return render(request, 'painel/produto_form.html', {
        'form': form, 'produto': produto, 'titulo': f'Editar: {produto.nome}'
    })


@staff_required
def produto_deletar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        nome = produto.nome
        produto.delete()
        messages.success(request, f'Produto "{nome}" removido.')
        return redirect('painel:produtos')
    from django.urls import reverse
    return render(request, 'painel/confirmar_exclusao.html', {
        'objeto': produto, 'cancel_url': reverse('painel:produtos')
    })


@staff_required
def categorias_lista(request):
    categorias = Categoria.objects.all()
    return render(request, 'painel/categorias_lista.html', {'categorias': categorias})


@staff_required
def categoria_criar(request):
    form = CategoriaForm(request.POST or None)
    if form.is_valid():
        cat = form.save()
        messages.success(request, f'Categoria "{cat.nome}" criada!')
        return redirect('painel:categorias')
    return render(request, 'painel/categoria_form.html', {'form': form, 'titulo': 'Nova Categoria'})


@staff_required
def categoria_editar(request, pk):
    cat = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=cat)
    if form.is_valid():
        cat = form.save()
        messages.success(request, f'Categoria "{cat.nome}" atualizada!')
        return redirect('painel:categorias')
    return render(request, 'painel/categoria_form.html', {
        'form': form, 'categoria': cat, 'titulo': f'Editar: {cat.nome}'
    })


@staff_required
def categoria_deletar(request, pk):
    cat = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nome = cat.nome
        cat.delete()
        messages.success(request, f'Categoria "{nome}" removida.')
        return redirect('painel:categorias')
    from django.urls import reverse
    return render(request, 'painel/confirmar_exclusao.html', {
        'objeto': cat, 'cancel_url': reverse('painel:categorias')
    })


@staff_required
def pedidos_lista(request):
    status_filtro = request.GET.get('status', '')
    pedidos = Pedido.objects.prefetch_related('itens').all()
    if status_filtro:
        pedidos = pedidos.filter(status=status_filtro)
    context = {
        'pedidos': pedidos,
        'status_filtro': status_filtro,
        'status_choices': Pedido.STATUS_CHOICES,
    }
    return render(request, 'painel/pedidos_lista.html', context)


@staff_required
def pedido_detalhe(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    form = StatusPedidoForm(request.POST or None, instance=pedido)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Status atualizado!')
        return redirect('painel:pedido_detalhe', pk=pk)
    return render(request, 'painel/pedido_detalhe.html', {'pedido': pedido, 'form': form})


@staff_required
def configuracoes(request):
    config = Configuracao.get_config()
    form = ConfiguracaoForm(request.POST or None, request.FILES or None, instance=config)
    if form.is_valid():
        form.save()
        messages.success(request, 'Configurações salvas com sucesso!')
        return redirect('painel:configuracoes')
    return render(request, 'painel/configuracoes.html', {'form': form, 'config': config})
