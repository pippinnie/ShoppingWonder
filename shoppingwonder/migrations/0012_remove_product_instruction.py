# Generated by Django 4.0.1 on 2022-03-27 13:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingwonder', '0011_product_created'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='instruction',
        ),
    ]
