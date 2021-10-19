from django.db import models
from authentication.models import User
from collects.models import Item


class Followers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'item')

    def __str__(self):
        return f'{self.user.username} likes {self.item.item_name}'
