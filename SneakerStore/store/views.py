from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q, Sum, F
from django.db.models.functions import Cast
from django.db.models import CharField
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect

from datetime import timedelta
import os

from .models import (
    Sneaker, Carrinho, ItemCarrinho, ItemEncomenda,
    Encomenda, Marca, Cliente, Tamanho, Categoria,
    EmpregadoLoja, Favoritos
)


def check_empregado_loja(user):
    return EmpregadoLoja.objects.filter(user_id=user.id).exists()


def check_cliente(user):
    return Cliente.objects.filter(user_id=user.id).exists()


def index(request):
    popular_sneakers = (
        Sneaker.objects.annotate(num_sales=Count('itemencomenda'))
        .order_by('-num_sales')[:8]
    )

    more_sneakers = Sneaker.objects.exclude(id__in=[s.id for s in popular_sneakers])[:4]

    context = {
        'popular_sneakers': popular_sneakers,
        'more_sneakers': more_sneakers,
    }

    return render(request, 'store/index.html', context)


@csrf_protect
def registar(request):
    if request.method == 'POST':

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

        if not all([nome, email, password, morada, telemovel, nif, categoria_preferida, tamanho_preferido,
                    marca_preferida]):
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            return redirect('store:registar')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Este email já está em uso. Por favor, tente outro.')
            return redirect('store:registar')

        if Cliente.objects.filter(nif=nif).exists():
            messages.error(request, 'Este NIF já está em uso. Por favor, tente outro.')
            return redirect('store:registar')

        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = nome
        user.save()

        Cliente.objects.create(user=user, morada=morada, telemovel=telemovel, nif=nif, imagem=imagem,
                               categoria_preferida_id=categoria_preferida,
                               tamanho_preferido_id=tamanho_preferido, marca_preferida_id=marca_preferida)

        user = authenticate(username=email, password=password)
        login(request, user)

        messages.success(request, 'Registo concluído com sucesso! Bem-vindo(a) à Sneaker Store.')
        return redirect('store:index')

    else:

        marcas = Marca.objects.all()

        tamanhos = Tamanho.objects.all()

        categorias = Categoria.objects.all()

        context = {
            'marcas': marcas,
            'tamanhos': tamanhos,
            'categorias': categorias,
        }

        return render(request, 'store/registo.html', context)


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login efetuado com sucesso!')

            if check_empregado_loja(user):
                return redirect('store:catalogo')
            else:
                return redirect('store:index')
        else:
            messages.error(request, 'Email ou senha incorretos. Por favor, tente novamente.')
            return redirect('store:login_view')
    else:
        return render(request, 'store/login.html')


@login_required
def perfil(request):
    return render(request, 'store/perfil.html')


@user_passes_test(check_cliente, login_url=reverse_lazy('store:login_view'))
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


@user_passes_test(check_cliente, login_url=reverse_lazy('store:login_view'))
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
            messages.info(request, f'O Sneaker {sneaker.nome} já está no carrinho! Quantidade atualizada.')
        except ItemCarrinho.DoesNotExist:
            # Se o item não estiver no carrinho, criar um novo item com quantidade 1
            item = ItemCarrinho.objects.create(carrinho=carrinho, sneaker=sneaker, quantidade=quantidade)
            messages.success(request, f'O Sneaker {sneaker.nome} foi adicionado ao carrinho!')

        # Colocar o carrinho na sessão
        request.session['carrinho_id'] = carrinho.id

        # Redirecionar para a página de onde veio o request
        return redirect(request.META.get('HTTP_REFERER', 'store:index'))


@login_required(login_url='store:login_view')
def favoritos(request):
    try:

        favoritos = Favoritos.objects.get(cliente=request.user.cliente)
    except Favoritos.DoesNotExist:

        messages.error(request, 'Parece que ainda não adicionou nenhum sneaker aos favoritos...')
        return redirect('store:index')

    context = {'favoritos': favoritos}
    return render(request, 'store/favoritos.html', context)


@user_passes_test(check_cliente, login_url=reverse_lazy('store:login_view'))
def adicionar_favoritos(request, sneaker_id):
    if request.method == "POST":
        sneaker = get_object_or_404(Sneaker, pk=sneaker_id)
        cliente = request.user.cliente

        try:
            favoritos = Favoritos.objects.get(cliente=cliente)
        except Favoritos.DoesNotExist:

            favoritos = Favoritos.objects.create(cliente=cliente)

        if favoritos.sneaker.filter(id=sneaker.id).exists():
            messages.info(request, f'O Sneaker {sneaker.nome} já está na sua lista de favoritos!')
        else:
            favoritos.sneaker.add(sneaker)
            favoritos.save()
            messages.success(request, f'O Sneaker {sneaker.nome} foi adicionado aos seus favoritos!')

        return redirect(request.META.get('HTTP_REFERER', 'store:index'))


@user_passes_test(check_cliente, login_url='store:login_view')
def remover_favoritos(request, sneaker_id):
    if request.method == "POST":
        sneaker = get_object_or_404(Sneaker, pk=sneaker_id)
        cliente = request.user.cliente

        try:
            favoritos = Favoritos.objects.get(cliente=cliente)
        except Favoritos.DoesNotExist:
            messages.info(request, 'Não tem nenhum favorito para remover.')
            return redirect('store:favoritos')

        if favoritos.sneaker.filter(id=sneaker.id).exists():
            favoritos.sneaker.remove(sneaker)
            messages.success(request, f'O Sneaker {sneaker.nome} foi removido dos favoritos!')
        else:
            messages.info(request, f'O Sneaker {sneaker.nome} não está na sua lista de favoritos.')

        return redirect('store:favoritos')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logout efetuado com sucesso!')
    return redirect('store:index')


@user_passes_test(check_cliente, login_url=reverse_lazy('store:login_view'))
def remover_carrinho(request, sneaker_id):
    try:
        sneaker = get_object_or_404(Sneaker, id=sneaker_id)

        carrinho = Carrinho.objects.filter(cliente=request.user.cliente, ativo=True).first()

        ItemCarrinho.objects.filter(carrinho=carrinho, sneaker=sneaker).delete()

        messages.success(request, f'O Sneaker {sneaker.nome} foi removido com sucesso do carrinho')
    except ItemCarrinho.DoesNotExist:
        messages.error(request, f'Houve um erro ao tentar remover o Sneaker {sneaker.nome} do carrinho')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro inesperado: {str(e)}')

    return redirect(reverse('store:carrinho'))


@user_passes_test(check_cliente, login_url=reverse_lazy('store:login_view'))
def finalizar_compra(request):
    carrinho = Carrinho.objects.filter(cliente=request.user.cliente, ativo=True).first()
    if not carrinho:
        return redirect('store:carrinho')

    data_atual = timezone.now().date()
    if carrinho.data_inatividade < data_atual:
        carrinho.ativo = False
        carrinho.save()
        messages.error(request, 'O seu carrinho expirou. Por favor, adicione os sneakers novamente.')
        return redirect('store:index')

    itens_carrinho = carrinho.itemcarrinho_set.select_related('sneaker').all()

    try:
        # Criar a encomenda
        nova_encomenda = Encomenda.objects.create(cliente=request.user.cliente, data=timezone.now(),
                                                  status='Em Processamento')

        # Atualizar o stock dos sneakers vendidos e criar os itens da encomenda
        for item in itens_carrinho:
            if item.quantidade > item.sneaker.quantidade_stock:
                messages.error(request,
                               f"O Sneaker '{item.sneaker.nome}' não existe em stock suficiente para a quantidade desejada.")
                return redirect('store:carrinho')
            item.sneaker.quantidade_stock -= item.quantidade
            item.sneaker.save()
            ItemEncomenda.objects.create(encomenda=nova_encomenda, sneaker=item.sneaker, quantidade=item.quantidade)

        # Limpar o carrinho
        carrinho.itemcarrinho_set.all().delete()
        carrinho.ativo = False
        carrinho.save()

    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao processar a sua compra: {e}. Por favor, tente novamente.')
        return redirect('store:carrinho')

    messages.success(request, 'A sua compra foi finalizada com sucesso.')
    return redirect('store:encomendas')


def catalogo(request):
    brand_filter = request.GET.get('brand')
    category_filter = request.GET.get('category')
    size_filter = request.GET.get('size')
    search_query = request.GET.get('search')

    sneakers = Sneaker.objects.all()

    if brand_filter:
        sneakers = sneakers.filter(marca__id=brand_filter)

    if category_filter:
        sneakers = sneakers.filter(categoria__id=category_filter)

    if size_filter:
        sneakers = sneakers.filter(tamanho__id=size_filter)

    if search_query:
        sneakers = sneakers.filter(nome__icontains=search_query)

    brands = Marca.objects.all()
    categories = Categoria.objects.all()
    sizes = Tamanho.objects.all()

    paginator = Paginator(sneakers, 16)
    page = request.GET.get('page')

    try:
        sneakers = paginator.page(page)
    except PageNotAnInteger:

        sneakers = paginator.page(1)
    except EmptyPage:

        sneakers = paginator.page(paginator.num_pages)

    if not sneakers:
        messages.info(request, 'Não foram encontrados resultados para a sua pesquisa.')

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


@login_required(login_url='store:login_view')
def editar_perfil(request):
    if request.method == 'POST':
        user = request.user

        nome = request.POST['nome']
        morada = request.POST['morada']
        telemovel = request.POST['telemovel']
        imagem = request.FILES['imagem'] if 'imagem' in request.FILES else None

        user.first_name = nome
        user.save()

        if check_cliente(user):
            cliente = Cliente.objects.get(user=user)
            categoria_preferida = request.POST['categoria_preferida']
            tamanho_preferido = request.POST['tamanho_preferido']
            marca_preferida = request.POST['marca_preferida']

            cliente.morada = morada
            cliente.telemovel = telemovel
            cliente.categoria_preferida_id = categoria_preferida
            cliente.tamanho_preferido_id = tamanho_preferido
            cliente.marca_preferida_id = marca_preferida

        elif check_empregado_loja(user):
            empregadoloja = EmpregadoLoja.objects.get(user=user)
cd
            empregadoloja.morada = morada
            empregadoloja.telemovel = telemovel

        if imagem:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'utilizadores'))
            filename = fs.save(imagem.name, imagem)
            if check_cliente(user):
                cliente.imagem = os.path.join('media/utilizadores', filename)
            elif check_empregado_loja(user):
                empregadoloja.imagem = os.path.join('media/utilizadores', filename)

        if check_cliente(user):
            cliente.save()
        elif check_empregado_loja(user):
            empregadoloja.save()

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
    search_query = request.GET.get('search', '')
    encomendas = Encomenda.objects.annotate(str_id=Cast('id', CharField())).order_by('-data')

    if check_empregado_loja(request.user):
        if search_query:
            encomendas = encomendas.filter(Q(cliente__user__username__icontains=search_query) |
                                           Q(status__icontains=search_query) |
                                           Q(str_id__icontains=search_query))
    elif check_cliente(request.user):
        encomendas = encomendas.filter(cliente=request.user.cliente)
        if search_query:
            encomendas = encomendas.filter(Q(status__icontains=search_query) |
                                           Q(str_id__icontains=search_query))

    for encomenda in encomendas:
        encomenda.total = 0
        for item in encomenda.itemencomenda_set.all():
            encomenda.total += item.sneaker.preco * item.quantidade

    if search_query and not encomendas:
        messages.info(request, 'Não foram encontrados resultados para a sua pesquisa.')

    context = {
        'encomendas': encomendas,
    }

    return render(request, 'store/encomendas.html', context)


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
        messages.success(request, f'O Sneaker {sneaker.nome} foi editado com sucesso!')
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
        messages.success(request, f'O Sneaker {sneaker.nome} foi removido com sucesso!')
        return redirect('store:catalogo')
    else:
        messages.error(f'Não foi possível remover o sneaker {sneaker.nome}')
        return redirect('store:catalogo')


@login_required
@user_passes_test(check_empregado_loja, login_url=reverse_lazy('store:login_view'))
def adicionar_sneaker(request):
    marcas = Marca.objects.all()
    categorias = Categoria.objects.all()
    tamanhos = Tamanho.objects.all()

    if request.method == 'GET':
        return render(request, 'store/adicionar_sneaker.html',
                      {'marcas': marcas, 'categorias': categorias, 'tamanhos': tamanhos})

    elif request.method == 'POST':
        nome = request.POST.get('nome', '')
        marca_id = request.POST.get('marca', '')
        categoria_id = request.POST.get('categoria', '')
        tamanho_id = request.POST.get('tamanho', '')
        preco = request.POST.get('preco', '')
        imagem = request.FILES.get('imagem', None)
        quantidade_stock = request.POST.get('stock', '')

        if nome and marca_id and categoria_id and tamanho_id and preco and imagem and quantidade_stock:
            try:
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'sneakers'))
                filename = fs.save(imagem.name, imagem)
                imagem = os.path.join('media/sneakers', filename)
                marca = Marca.objects.get(pk=marca_id)
                categoria = Categoria.objects.get(pk=categoria_id)
                tamanho = Tamanho.objects.get(pk=tamanho_id)

                sneaker = Sneaker(nome=nome, marca=marca, categoria=categoria, tamanho=tamanho, preco=preco,
                                  imagem=imagem, quantidade_stock=quantidade_stock)
                sneaker.save()

                messages.success(request, f'O Sneaker {sneaker.nome} foi adicionado com sucesso!')
                return redirect('store:catalogo')

            except Exception as e:
                messages.error(request, f'Erro ao adicionar o sneaker {sneaker.nome}')
        else:
            messages.error(request, 'Todos os campos são obrigatórios.')

        return render(request, 'store/adicionar_sneaker.html',
                      {'marcas': marcas, 'categorias': categorias, 'tamanhos': tamanhos})


@login_required(login_url='store:login_view')
def update_encomenda_status(request, encomenda_id):
    if not check_empregado_loja(request.user):
        return HttpResponseForbidden()

    encomenda = get_object_or_404(Encomenda, id=encomenda_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status in dict(Encomenda.STATUS_CHOICES):
            encomenda.status = new_status
            encomenda.save()
            messages.success(request, f'Status da encomenda {encomenda.id} trocado com sucesso')

    return redirect(reverse('store:encomendas'))


@login_required(login_url='store:login_view')
def recomendados(request):
    if not check_cliente(request.user):
        return HttpResponseForbidden()

    cliente = Cliente.objects.get(user=request.user)
    sneakers = Sneaker.objects.filter(
        marca=cliente.marca_preferida,
        categoria=cliente.categoria_preferida,
        tamanho=cliente.tamanho_preferido
    )

    return render(request, 'store/recomendados.html', {'sneakers': sneakers})
