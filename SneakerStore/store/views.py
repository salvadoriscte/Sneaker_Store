from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Sneaker, Carrinho, ItemCarrinho, ItemEncomenda, Encomenda, Marca, Cliente, Tamanho, Categoria, \
    EmpregadoLoja
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


def index(request):
    # Get popular sneakers
    popular_sneakers = (
        Sneaker.objects.annotate(num_sales=Count('itemencomenda'))
        .order_by('-num_sales')[:8]
    )
    more_sneakers = Sneaker.objects.all()[4:8]

    context = {
        'popular_sneakers': popular_sneakers,
        'more_sneakers': more_sneakers,
    }

    return render(request, 'store/index.html', context)


def registar(request):
    if request.method == 'POST':
        # get form data
        nome = request.POST['nome']
        email = request.POST['email']
        password = request.POST['password']
        morada = request.POST['morada']
        telemovel = request.POST['telemovel']
        nif = request.POST['nif']
        imagem = request.FILES['imagem'] if 'imagem' in request.FILES else None
        categoria_preferida = request.POST['categoria_preferida']
        tamanho_preferido = request.POST['tamanho_preferido']
        marca_preferida = request.POST['marca_preferida']

        # check if any required field is missing
        if not all([nome, email, password, morada, telemovel, nif, categoria_preferida, tamanho_preferido,
                    marca_preferida]):
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            return redirect('store:registar')

        # check if the user already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Este email já está em uso. Por favor, tente outro.')
            return redirect('store:registar')

        # check if the NIF already exists
        if Cliente.objects.filter(nif=nif).exists():
            messages.error(request, 'Este NIF já está em uso. Por favor, tente outro.')
            return redirect('store:registar')

        # create user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = nome
        user.save()

        # create client
        cliente = Cliente.objects.create(user=user, morada=morada, telemovel=telemovel, nif=nif, imagem=imagem,
                                         categoria_preferida_id=categoria_preferida,
                                         tamanho_preferido_id=tamanho_preferido, marca_preferida_id=marca_preferida)

        # log in the user
        user = authenticate(username=email, password=password)
        login(request, user)

        # redirect to the user's profile page
        return redirect('store:perfil')

    else:
        # get all brands from the database
        marcas = Marca.objects.all()
        # get all sizes from the database
        tamanhos = Tamanho.objects.all()
        # get all categories from the database
        categorias = Categoria.objects.all()

        # pass the brands, sizes, and categories to the template context
        context = {
            'marcas': marcas,
            'tamanhos': tamanhos,
            'categorias': categorias,
        }

        return render(request, 'store/registo.html', context)



def login_view(request):  # não se pode chamar login pq da conflito!!!!!!!
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('store:index')
        else:
            messages.error(request, 'Email ou senha incorretos. Por favor, tente novamente.')
            return redirect('store:login')
    else:
        return render(request, 'store/login.html')

@login_required
def perfil(request):
    return render(request, 'store/perfil.html')


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
