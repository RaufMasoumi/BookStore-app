# Generated by Django 4.0.5 on 2022-07-24 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_alter_book_category_delete_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reviewreply',
            name='author',
        ),
        migrations.RemoveField(
            model_name='reviewreply',
            name='review',
        ),
        migrations.RemoveField(
            model_name='reviewreply',
            name='to',
        ),
        migrations.DeleteModel(
            name='Review',
        ),
        migrations.DeleteModel(
            name='ReviewReply',
        ),
    ]