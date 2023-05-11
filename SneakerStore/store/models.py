from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, timedelta


class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    morada = models.CharField(max_length=255)
    telemovel = models.IntegerField()
    nif = models.IntegerField()
    imagem = models.ImageField(default='store/images/default_profile_pic.png')
    categoria_preferida = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True)
    tamanho_preferido = models.ForeignKey('Tamanho', on_delete=models.SET_NULL, null=True)
    marca_preferida = models.ForeignKey('Marca', on_delete=models.SET_NULL, null=True)


class EmpregadoLoja(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    morada = models.CharField(max_length=255)
    nif = models.IntegerField()
    telemovel = models.IntegerField()
    imagem = models.ImageField(default='store/images/default_profile_pic.png')


class Marca(models.Model):
    nome = models.CharField(max_length=255)
    pais = models.CharField(max_length=255)


class Tamanho(models.Model):
    tamanho = models.CharField(max_length=50)


class Categoria(models.Model):
    nome = models.CharField(max_length=255)


class Sneaker(models.Model):
    nome = models.CharField(max_length=255)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True)
    tamanho = models.ForeignKey(Tamanho, on_delete=models.CASCADE)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem = models.ImageField()
    quantidade_stock = models.IntegerField()


class Carrinho(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE)
    ativo = models.BooleanField()
    data_inatividade = models.DateField(default=datetime.now() + timedelta(days=7))


class ItemCarrinho(models.Model):
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE)
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE)
    quantidade = models.IntegerField()


class Encomenda(models.Model):
    STATUS_CHOICES = [
        ('processamento', 'Em Processamento'),
        ('cancelada', 'Cancelada'),
        ('entregue', 'Entregue'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data = models.DateTimeField()
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)


class ItemEncomenda(models.Model):
    encomenda = models.ForeignKey(Encomenda, on_delete=models.CASCADE)
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE)
    quantidade = models.IntegerField()


class Favoritos(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    sneaker = models.ManyToManyField(Sneaker)
