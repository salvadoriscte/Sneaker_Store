# Generated by Django 4.2 on 2023-04-11 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_cliente_marca_preferida_alter_cliente_imagem_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='imagem',
            field=models.ImageField(blank=True, default='store/images/default_profile_pic.png', null=True, upload_to='store/images/clientes/'),
        ),
    ]
