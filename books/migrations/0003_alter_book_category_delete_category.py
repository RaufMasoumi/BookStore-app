# Generated by Django 4.0.5 on 2022-07-24 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
        ('books', '0002_alter_book_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='category',
            field=models.ManyToManyField(blank=True, related_name='books', to='categories.category'),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]
