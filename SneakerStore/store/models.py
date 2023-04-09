from django.contrib.auth.models import User
from django.db import models

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    morada = models.CharField(max_length=255)
    telemovel = models.IntegerField()
    nif = models.IntegerField()
    imagem = models.ImageField(upload_to='clientes/')
    categoria_preferida = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True)
    tamanho_preferido = models.ForeignKey('Tamanho', on_delete=models.SET_NULL, null=True)

class PreferenciaMarca(models.Model):

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    marca = models.ForeignKey('Marca', on_delete=models.CASCADE)

class EmpregadoLoja(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    morada = models.CharField(max_length=255)
    nif = models.IntegerField()
    telemovel = models.IntegerField()

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
    imagem = models.ImageField(upload_to='store/images/')
    quantidade_stock = models.IntegerField()

class Carrinho(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE)
    ativo = models.BooleanField()
    data_inatividade = models.DateField()

class ItemCarrinho(models.Model):
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE)
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE)
    quantidade = models.IntegerField()

class Encomenda(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data = models.DateTimeField()
    status = models.CharField(max_length=255)

class ItemEncomenda(models.Model):
    encomenda = models.ForeignKey(Encomenda, on_delete=models.CASCADE)
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
