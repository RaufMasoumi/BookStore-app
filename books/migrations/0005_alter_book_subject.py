# Generated by Django 4.0.5 on 2023-07-15 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_remove_reviewreply_author_remove_reviewreply_review_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='subject',
            field=models.TextField(blank=True, null=True),
        ),
    ]
