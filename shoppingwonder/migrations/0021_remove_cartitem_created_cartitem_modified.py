# Generated by Django 4.0.3 on 2022-04-03 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingwonder', '0020_cartitem_delete_cart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='created',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]