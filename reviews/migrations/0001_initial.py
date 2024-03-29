# Generated by Django 4.0.5 on 2022-07-24 08:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('books', '0004_remove_reviewreply_author_remove_reviewreply_review_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='guest', max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('review', models.TextField(max_length=250)),
                ('rating', models.FloatField(blank=True, default=0)),
                ('submitted', models.DateTimeField(auto_now_add=True)),
                ('votes', models.IntegerField(blank=True, default=0)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='books.book')),
            ],
            options={
                'ordering': ['votes', '-submitted'],
            },
        ),
        migrations.CreateModel(
            name='ReviewReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='guest', max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('reply', models.CharField(max_length=250)),
                ('replied', models.DateTimeField(auto_now_add=True)),
                ('votes', models.IntegerField(default=0)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='reviews.review')),
                ('to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='reviews.reviewreply')),
            ],
            options={
                'verbose_name_plural': 'Review Replies',
                'ordering': ['votes', '-replied'],
            },
        ),
    ]
