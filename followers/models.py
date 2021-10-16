from django.db import models
from authentication.models import User


# Create your models here.
from collects.models import Collect


class Followers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collect, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'collection',)

    def __str__(self):
        return f'{self.user.id} following {self.collection.id}'
