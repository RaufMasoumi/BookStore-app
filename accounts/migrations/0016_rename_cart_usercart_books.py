# Generated by Django 4.0.3 on 2022-03-09 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_alter_usercart_user_userwish'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usercart',
            old_name='cart',
            new_name='books',
        ),
    ]