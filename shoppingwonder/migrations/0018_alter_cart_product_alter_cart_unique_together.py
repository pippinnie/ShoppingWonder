# Generated by Django 4.0.3 on 2022-04-03 05:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingwonder', '0017_remove_cart_products_cart_product_cart_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='shoppingwonder.product'),
        ),
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together={('shopper', 'product')},
        ),
    ]
