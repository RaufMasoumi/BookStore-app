# Generated by Django 4.0.3 on 2022-04-12 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0050_book_views'),
        ('accounts', '0018_alter_useraddress_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useraddress',
            name='address',
        ),
        migrations.AddField(
            model_name='useraddress',
            name='city',
            field=models.CharField(default='urmia', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='useraddress',
            name='country',
            field=models.CharField(default='Iran', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='useraddress',
            name='no',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='useraddress',
            name='postal_code',
            field=models.CharField(default='235435234243', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='useraddress',
            name='reciever_first_name',
            field=models.CharField(default='Rauf', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='useraddress',
            name='reciever_last_name',
            field=models.CharField(default='Masoumi', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='useraddress',
            name='reciever_phone_number',
            field=models.CharField(default='09019860448', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='useraddress',
            name='street',
            field=models.CharField(default='Shahid naser elyasi', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userwish',
            name='books',
            field=models.ManyToManyField(blank=True, related_name='in_wishlists', to='books.book'),
        ),
    ]