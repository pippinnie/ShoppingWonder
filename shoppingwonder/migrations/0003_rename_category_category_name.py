# Generated by Django 4.0.1 on 2022-03-20 15:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingwonder', '0002_alter_product_variations_alter_product_watchers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='category',
            new_name='name',
        ),
    ]
