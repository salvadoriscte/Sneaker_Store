# Generated by Django 4.2 on 2023-05-08 17:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_alter_carrinho_data_inatividade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrinho',
            name='data_inatividade',
            field=models.DateField(default=datetime.datetime(2023, 5, 15, 18, 58, 28, 998453)),
        ),
        migrations.AlterField(
            model_name='sneaker',
            name='imagem',
            field=models.ImageField(upload_to='store/imagens/'),
        ),
    ]
