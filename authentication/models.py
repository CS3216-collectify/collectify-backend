from django.db import models
from django.contrib.auth.models import AbstractUser


# This model behaves identically to the default user model, but you’ll be able to customize
# it in the future if the need arises.
class User(AbstractUser):
    # Add any properties here that is not already in the default django user.
    email = models.EmailField(unique=True)
    picture_file = models.ImageField(upload_to='profile_images', null=True, blank=True)

    def picture_url(self):
        if self.picture_file and hasattr(self.picture_file, 'url'):
            return self.picture_file.url
