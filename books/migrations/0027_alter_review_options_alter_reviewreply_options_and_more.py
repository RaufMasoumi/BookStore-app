# Generated by Django 4.0.1 on 2022-01-26 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0026_rename_active_category_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['-submitted']},
        ),
        migrations.AlterModelOptions(
            name='reviewreply',
            options={'ordering': ['-replied'], 'verbose_name_plural': 'ReviewReplies'},
        ),
        migrations.AddField(
            model_name='reviewreply',
            name='add',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='books.reviewreply'),
        ),
        migrations.AlterField(
            model_name='category',
            name='thumbnail',
            field=models.ImageField(blank=True, upload_to='categories'),
        ),
    ]