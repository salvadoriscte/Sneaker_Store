# Generated by Django 4.2 on 2023-05-08 18:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0020_alter_carrinho_data_inatividade_alter_cliente_imagem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrinho',
            name='data_inatividade',
            field=models.DateField(default=datetime.datetime(2023, 5, 15, 19, 41, 36, 592469)),
        ),
    ]
