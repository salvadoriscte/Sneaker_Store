# Generated by Django 4.2 on 2023-05-08 19:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0022_alter_carrinho_data_inatividade_alter_sneaker_imagem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrinho',
            name='data_inatividade',
            field=models.DateField(default=datetime.datetime(2023, 5, 15, 20, 8, 18, 240176)),
        ),
        migrations.AlterField(
            model_name='sneaker',
            name='imagem',
            field=models.ImageField(upload_to='sneakers/'),
        ),
    ]