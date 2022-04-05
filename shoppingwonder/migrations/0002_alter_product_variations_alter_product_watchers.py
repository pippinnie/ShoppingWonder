# Generated by Django 4.0.1 on 2022-03-20 15:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingwonder', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='variations',
            field=models.ManyToManyField(blank=True, related_name='products', to='shoppingwonder.AttributeValue'),
        ),
        migrations.AlterField(
            model_name='product',
            name='watchers',
            field=models.ManyToManyField(blank=True, related_name='favorites', to=settings.AUTH_USER_MODEL),
        ),
    ]
