# Generated by Django 4.0.1 on 2022-01-10 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0008_alter_book_id'),
        ('accounts', '0003_alter_usercart_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercart',
            name='cart',
            field=models.ManyToManyField(blank=True, null=True, related_name='in_carts', to='books.Book'),
        ),
    ]
