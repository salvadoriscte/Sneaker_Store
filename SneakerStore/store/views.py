from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Sneaker, Carrinho, ItemCarrinho, ItemEncomenda, Encomenda, Marca, Cliente, Tamanho, Categoria,EmpregadoLoja, Favoritos
from django.db.models import Count, Q, Sum, F
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from datetime import datetime, timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import FileSystemStorage
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings


def check_empregado_loja(user):
    return EmpregadoLoja.objects.filter(user_id=user.id).exists()


def check_cliente(user):
    return Cliente.objects.filter(user_id=user.id).exists()


def index(request):
    # Get popular sneakers
    popular_sneakers = (
        Sneaker.objects.annotate(num_sales=Count('itemencomenda'))
        .order_by('-num_sales')[:8]
    )

    # Get more sneakers
    more_sneakers = Sneaker.objects.exclude(id__in=[s.id for s in popular_sneakers])[:4]

    context = {
        'popular_sneakers': popular_sneakers,
        'more_sneakers': more_sneakers,
    }

    return render(request, 'store/index.html', context)


@csrf_protect
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
        messages.success(request, 'Registo concluído com sucesso! Bem-vindo(a) à Sneaker Store.')
        return redirect('store:index')

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
        print(email, password)
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login efetuado com sucesso!')
            return redirect('store:index')
        else:
            print(user)
            messages.error(request, 'Email ou senha incorretos. Por favor, tente novamente.')
            return redirect('store:login_view')
    else:
        return render(request, 'store/login.html')


@login_required
def perfil(request):
    return render(request, 'store/perfil.html')


@login_required(login_url=reverse_lazy('store:login_view'))
def carrinho(request):
    carrinho = Carrinho.objects.filter(cliente=request.user.cliente, ativo=True).first()
    if not carrinho:
        return render(request, 'store/carrinho.html', {'itens_carrinho': [], 'cart_total': 0})

    data_atual = timezone.now().date()
    if carrinho.data_inatividade < data_atual:
        carrinho.ativo = False
        carrinho.save()
        novo_carrinho = Carrinho.objects.create(cliente=request.user.cliente, ativo=True)
        carrinho = novo_carrinho

    itens_carrinho = carrinho.itemcarrinho_set.select_related('sneaker').all().prefetch_related('sneaker')

    total_carrinho = itens_carrinho.aggregate(total_carrinho=Sum(F('quantidade') * F('sneaker__preco')))[
                         'total_carrinho'] or 0

    itens_carrinho = itens_carrinho.annotate(total_item=F('quantidade') * F('sneaker__preco'))

    context = {
        'itens_carrinho': itens_carrinho,
        'total_carrinho': total_carrinho,
    }
    return render(request, 'store/carrinho.html', context)


@login_required(login_url=reverse_lazy('store:login_view'))
def adicionar_carrinho(request, sneaker_id):
    if request.method == "POST":
        sneaker = get_object_or_404(Sneaker, pk=sneaker_id)
        cliente = request.user.cliente
        quantidade = int(request.POST.get(f"quantidade-{sneaker_id}", 1))

        # Verificar se o carrinho existe para o cliente logado
        try:
            carrinho = Carrinho.objects.get(cliente=cliente, ativo=True)
        except Carrinho.DoesNotExist:
            # Se o carrinho não existir, verificar se existe algum carrinho inativo
            try:
                carrinho = Carrinho.objects.get(cliente=cliente, ativo=False)
                carrinho.ativo = True
            except Carrinho.DoesNotExist:
                # Se não houver carrinho inativo, criar um novo carrinho
                carrinho = Carrinho(cliente=cliente, ativo=True)

        # Atualizar a data de inatividade do carrinho
        carrinho.data_inatividade = timezone.now() + timedelta(days=7)
        carrinho.save()

        # Verificar se o item já está no carrinho
        try:
            item = ItemCarrinho.objects.get(carrinho=carrinho, sneaker=sneaker)
            item.quantidade += quantidade
            item.save()
            messages.info(request, f'{sneaker.nome} já está no carrinho! Quantidade atualizada.')
        except ItemCarrinho.DoesNotExist:
            # Se o item não estiver no carrinho, criar um novo item com quantidade 1
            item = ItemCarrinho.objects.create(carrinho=carrinho, sneaker=sneaker, quantidade=quantidade)
            messages.success(request, f'{sneaker.nome} foi adicionado ao carrinho!')

        # Setar o carrinho na sessão
        request.session['carrinho_id'] = carrinho.id

        # Redirecionar para a página do carrinho
        return redirect('store:carrinho')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logout efetuado com sucesso!')
    return redirect('store:index')


@login_required(login_url=reverse_lazy('store:login_view'))
def remove_from_cart(request, sneaker_id):
    sneaker = get_object_or_404(Sneaker, id=sneaker_id)

    carrinho = Carrinho.objects.filter(cliente=request.user.cliente, ativo=True).first()

    ItemCarrinho.objects.filter(carrinho=carrinho, sneaker=sneaker).delete()

    return redirect(reverse('store:carrinho'))


@login_required(login_url=reverse_lazy('store:login_view'))
def finalizar_compra(request):
    carrinho = Carrinho.objects.filter(cliente=request.user.cliente, ativo=True).first()
    if not carrinho:
        return redirect('store:carrinho')

    data_atual = timezone.now().date()
    if carrinho.data_inatividade < data_atual:
        carrinho.ativo = False
        carrinho.save()
        messages.error(request, 'O seu carrinho expirou. Por favor, adicione os produtos novamente.')
        return redirect('store:index')

    itens_carrinho = carrinho.itemcarrinho_set.select_related('sneaker').all()

    try:
        # Criar a encomenda
        nova_encomenda = Encomenda.objects.create(cliente=request.user.cliente, data=timezone.now(),
                                                  status='Em processamento')

        # Atualizar o stock dos sneakers vendidos e criar os itens da encomenda
        for item in itens_carrinho:
            if item.quantidade > item.sneaker.quantidade_stock:
                messages.error(request,
                               f"O produto '{item.sneaker.nome}' não tem stock suficiente para a quantidade desejada.")
                return redirect('store:carrinho')
            item.sneaker.quantidade_stock -= item.quantidade
            item.sneaker.save()
            ItemEncomenda.objects.create(encomenda=nova_encomenda, sneaker=item.sneaker, quantidade=item.quantidade)

        # Limpar o carrinho
        carrinho.itemcarrinho_set.all().delete()
        carrinho.ativo = False
        carrinho.save()

    except Exception as e:
        messages.error(request, 'Ocorreu um erro ao processar a sua compra. Por favor, tente novamente.')
        return redirect('store:carrinho')

    messages.success(request, 'A sua compra foi finalizada com sucesso.')
    return redirect('store:encomendas')


def catalogo(request):
    # Get filter parameters from the URL
    brand_filter = request.GET.get('brand')
    category_filter = request.GET.get('category')
    size_filter = request.GET.get('size')
    search_query = request.GET.get('search')

    # Filter the sneakers based on the selected filters and search query
    sneakers = Sneaker.objects.all()

    if brand_filter:
        sneakers = sneakers.filter(marca__id=brand_filter)

    if category_filter:
        sneakers = sneakers.filter(categoria__id=category_filter)

    if size_filter:
        sneakers = sneakers.filter(tamanho__id=size_filter)

    if search_query:
        sneakers = sneakers.filter(nome__icontains=search_query)

    # Get all brands, categories, and sizes for the filter dropdowns
    brands = Marca.objects.all()
    categories = Categoria.objects.all()
    sizes = Tamanho.objects.all()

    context = {
        'sneakers': sneakers,
        'brands': brands,
        'categories': categories,
        'sizes': sizes,
        'selected_brand': brand_filter,
        'selected_category': category_filter,
        'selected_size': size_filter,
        'search_query': search_query,
    }

    return render(request, 'store/catalogo.html', context)


def sobre_nos(request):
    return render(request, 'store/sobre_nos.html')


def detalhes(request, sneaker_id):
    sneaker = get_object_or_404(Sneaker, pk=sneaker_id)
    return render(request, 'store/detalhes.html', {'sneaker': sneaker})


@login_required
def editar_perfil(request):
    if request.method == 'POST':
        user = request.user
        cliente = request.user.cliente

        # Get form data
        nome = request.POST['nome']
        morada = request.POST['morada']
        telemovel = request.POST['telemovel']
        categoria_preferida = request.POST['categoria_preferida']
        tamanho_preferido = request.POST['tamanho_preferido']
        marca_preferida = request.POST['marca_preferida']
        imagem = request.FILES['imagem'] if 'imagem' in request.FILES else None

        # Update user and cliente data
        user.first_name = nome
        user.save()

        cliente.morada = morada
        cliente.telemovel = telemovel
        cliente.categoria_preferida_id = categoria_preferida
        cliente.tamanho_preferido_id = tamanho_preferido
        cliente.marca_preferida_id = marca_preferida
        if imagem:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'clientes'))
            filename = fs.save(imagem.name, imagem)
            cliente.imagem = os.path.join('media/clientes', filename)

        cliente.save()

        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('store:perfil')

    else:
        marcas = Marca.objects.all()
        tamanhos = Tamanho.objects.all()
        categorias = Categoria.objects.all()

        context = {
            'marcas': marcas,
            'tamanhos': tamanhos,
            'categorias': categorias,
        }
        return render(request, 'store/editar_perfil.html', context)


@login_required(login_url='store:login_view')
def encomendas(request):
    encomendas = Encomenda.objects.filter(cliente=request.user.cliente).order_by('-data')
    for encomenda in encomendas:
        encomenda.total = 0
        for item in encomenda.itemencomenda_set.all():
            encomenda.total += item.sneaker.preco * item.quantidade

    context = {
        'encomendas': encomendas
    }

    return render(request, 'store/encomendas.html', context)


# admin
# tenho que implementar esta funçoes e falta adicionar isto ao site
# falta melhorar o sobre nos
# ver a questao de como queres fazer o redirecionamento

#tenho que ver como é que vou fazer o painel de controlo mas para já fazer os botões



@login_required
@user_passes_test(check_empregado_loja, login_url=reverse_lazy('store:login_view'))
def painel_de_controlo(request):
    if not request.user.is_authenticated or not request.user.is_admin:
        return redirect('store:index')

    orders = Order.objects.all()
    sneakers = Sneaker.objects.all()
    context = {'orders': orders, 'sneakers': sneakers}
    return render(request, 'store/painel_de_controlo.html', context)


def update_order_status(request, order_id):
    # Implemente a lógica para atualizar o status do pedido aqui
    pass


def add_sneaker(request):
    # Implemente a lógica para adicionar um novo tênis aqui
    pass


@login_required
@user_passes_test(check_empregado_loja, login_url=reverse_lazy('store:login_view'))
def editar_sneaker(request, sneaker_id):
    sneaker = get_object_or_404(Sneaker, id=sneaker_id)
    if request.method == "POST":
        sneaker.nome = request.POST['nome']
        sneaker.marca_id = request.POST['marca']
        sneaker.categoria_id = request.POST['categoria']
        sneaker.tamanho_id = request.POST['tamanho']
        sneaker.preco = request.POST['preco']
        sneaker.quantidade_stock = request.POST['quantidade_stock']

        imagem = request.FILES.get('imagem')
        if imagem:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'sneakers'))
            filename = fs.save(imagem.name, imagem)
            sneaker.imagem = os.path.join('media/sneakers', filename)

        sneaker.save()
        messages.success(request, 'Sneaker editado com sucesso!')
        return redirect('store:detalhes', sneaker_id=sneaker.id)
    else:
        marcas = Marca.objects.all()
        categorias = Categoria.objects.all()
        tamanhos = Tamanho.objects.all()
        context = {'sneaker': sneaker, 'marcas': marcas, 'categorias': categorias, 'tamanhos': tamanhos}
        return render(request, 'store/editar_sneaker.html', context)

@login_required
@user_passes_test(check_empregado_loja, login_url=reverse_lazy('store:login_view'))
def remover_sneaker(request, sneaker_id):
    sneaker = get_object_or_404(Sneaker, id=sneaker_id)
    if request.user.is_authenticated and check_empregado_loja(request.user):
        sneaker.delete()
        messages.success(request, 'Sneaker removido com sucesso!')
        return redirect('store:index')
    else:
        messages.error('Erro ao remover Sneaker!')
        return redirect('store:index')