# Generated by Django 4.0.1 on 2022-01-10 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0009_alter_book_id'),
        ('accounts', '0005_customuser_cash_usercart_total_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercart',
            name='cart',
            field=models.ManyToManyField(blank=True, related_name='in_carts', to='books.Book'),
        ),
    ]