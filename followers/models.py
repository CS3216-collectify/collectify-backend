from django.db import models

from authentication.models import User
# Create your models here.
from collects.models import Collect


class Followers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collect, related_name='followers', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'collection',)

    def __str__(self):
        return f'{self.user.username} following {self.collection.collection_name}'
