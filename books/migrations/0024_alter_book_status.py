# Generated by Django 4.0.1 on 2022-01-25 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0023_alter_review_options_alter_reviewreply_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='status',
            field=models.CharField(choices=[('p', 'Published'), ('d', 'Draft')], max_length=1),
        ),
    ]