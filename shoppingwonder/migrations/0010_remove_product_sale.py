# Generated by Django 4.0.1 on 2022-03-26 17:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingwonder', '0009_remove_product_best_seller_remove_product_new'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='sale',
        ),
    ]
