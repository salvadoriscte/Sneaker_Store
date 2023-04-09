from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Sneaker, Carrinho, ItemCarrinho, ItemEncomenda, Encomenda

from django.db.models import Count,Q

def index(request):
    # Get popular sneakers
    popular_sneakers = (
        Sneaker.objects.annotate(num_sales=Count('itemencomenda'))
        .order_by('-num_sales')[:4]
    )
    more_sneakers = Sneaker.objects.all()[4:8]

    context = {
        'popular_sneakers': popular_sneakers,
        'more_sneakers': more_sneakers,
    }

    return render(request, 'store/index.html', context)
@login_required
def carrinho(request):
    carrinho = Carrinho.objects.filter(cliente=request.user.cliente, ativo=True).first()
    context = {
        'carrinho': carrinho,
    }
    return render(request, 'store/carrinho.html', context)


@login_required
def finalizar_compra(request):
    carrinho = Carrinho.objects.filter(cliente=request.user.cliente, ativo=True).first()

    if request.method == 'POST':
        # Create an order
        encomenda = Encomenda.objects.create(cliente=request.user.cliente)

        # Add the items from the cart to the order
        for item in carrinho.itemcarrinho_set.all():
            ItemEncomenda.objects.create(encomenda=encomenda, sneaker=item.sneaker, quantidade=item.quantidade)

        # Clear the cart
        carrinho.ativo = False
        carrinho.save()

        messages.success(request, 'Sua compra foi finalizada com sucesso!')
        return

@login_required
def add_to_cart(request, sneaker_id):
    sneaker = Sneaker.objects.get(pk=sneaker_id)

    # Verificar se o carrinho existe para o cliente logado
    carrinho, created = Carrinho.objects.get_or_create(cliente=request.user.cliente, ativo=True)

    # Verificar se o item já está no carrinho
    item, item_created = ItemCarrinho.objects.get_or_create(carrinho=carrinho, sneaker=sneaker)
    if not item_created:
        item.quantidade += 1
        item.save()

    messages.success(request, f'{sneaker.nome} foi adicionado ao carrinho!')
    return redirect('store:index')