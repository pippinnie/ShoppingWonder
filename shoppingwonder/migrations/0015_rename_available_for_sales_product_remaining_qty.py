# Generated by Django 4.0.1 on 2022-04-02 12:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingwonder', '0014_product_available_for_sales'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='available_for_sales',
            new_name='remaining_qty',
        ),
    ]
