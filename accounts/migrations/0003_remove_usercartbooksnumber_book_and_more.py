# Generated by Django 4.0.5 on 2022-07-24 09:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usercartbooksnumber',
            name='book',
        ),
        migrations.RemoveField(
            model_name='usercartbooksnumber',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='userwish',
            name='books',
        ),
        migrations.RemoveField(
            model_name='userwish',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserCart',
        ),
        migrations.DeleteModel(
            name='UserCartBooksNumber',
        ),
        migrations.DeleteModel(
            name='UserWish',
        ),
    ]