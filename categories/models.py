from django.db import models
from django.urls import reverse
# Create your models here.


class CategoryManager(models.Manager):

    def active(self):
        return self.filter(status=True)


class Category(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    title = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='categories', blank=True, max_length=300)
    status = models.BooleanField(default=True, verbose_name='To be displayed?')
    position = models.IntegerField()
    objects = CategoryManager()

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['parent_id', 'position']
        permissions = [
            ('category_list', 'Can see category list')
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_books_list', kwargs={'pk': self.pk})
