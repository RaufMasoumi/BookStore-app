# Generated by Django 4.0.1 on 2022-01-09 08:36

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_alter_book_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='id',
            field=models.UUIDField(default=uuid.UUID('09ef1ae8-8816-4f66-adf6-7e21e3c34d59'), editable=False, primary_key=True, serialize=False),
        ),
    ]