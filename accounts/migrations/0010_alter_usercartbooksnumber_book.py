# Generated by Django 4.0.1 on 2022-01-16 22:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0013_alter_book_id'),
        ('accounts', '0009_remove_usercart_total_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercartbooksnumber',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carts_numbers', to='books.book'),
        ),
    ]
