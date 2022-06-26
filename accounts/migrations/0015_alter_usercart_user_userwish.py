# Generated by Django 4.0.1 on 2022-03-01 19:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0049_book_mostpopular_alter_book_bestseller_and_more'),
        ('accounts', '0014_alter_customuser_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercart',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='UserWish',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('books', models.ManyToManyField(blank=True, to='books.Book')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='wish_list', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
