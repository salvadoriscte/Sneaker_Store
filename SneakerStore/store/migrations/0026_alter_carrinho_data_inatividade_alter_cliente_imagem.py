# Generated by Django 4.2 on 2023-05-08 19:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0025_alter_carrinho_data_inatividade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrinho',
            name='data_inatividade',
            field=models.DateField(default=datetime.datetime(2023, 5, 15, 20, 51, 35, 875081)),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='imagem',
            field=models.ImageField(default='store/images/default_profile_pic.png', upload_to=''),
        ),
    ]
