from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from config.settings import MEDIA_ROOT, MEDIA_URL
from allauth.socialaccount.models import SocialAccount
from cloudinary.uploader import upload
import re
import requests
# Create your models here.


class CustomUser(AbstractUser):
    image = models.ImageField(upload_to='accounts/pictures/', blank=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=200, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('account_user_detail')


class UserAddress(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='addresses')
    receiver_first_name = models.CharField(max_length=100)
    receiver_last_name = models.CharField(max_length=100)
    receiver_phone_number = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    no = models.PositiveIntegerField()
    postal_code = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'user addresses'

    def __str__(self):
        return f'{self.user}\'s address'

    def get_absolute_url(self):
        return reverse("user_address_detail", kwargs={'pk': self.pk})


@receiver(post_save, sender=SocialAccount)
def update_user_profile_image(instance, **kwargs):
    if instance.user.image:
        return
    image_url = instance.extra_data['picture']
    user = instance.user
    image_name = f'{user.username}.png'

    # development
    if MEDIA_URL == '/media/':
        response = requests.get(image_url)
        path = f'{MEDIA_ROOT}/accounts/pictures/' + image_name
        with open(path, 'wb') as image:
            image.write(response.content)
        user.image = path.split('media')[1]

    # production
    elif MEDIA_URL == '/rauf-bookstore-app/media/':
        public_id = re.sub(r'[?&#\\%<>+/\s+]', '_', repr(user.username)[1:-1])
        upload(image_url, public_id=public_id, folder='rauf-bookstore-app/media/accounts/pictures/', format='png')
        user.image = '/accounts/pictures/' + public_id + '.png'

    user.save()
    return
