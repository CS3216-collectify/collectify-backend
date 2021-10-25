from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum, Count
import functools


class User(AbstractUser):
    # Add any properties here that is not already in the default django user.
    email = models.EmailField(unique=True)
    picture_file = models.ImageField(upload_to='profile_images', null=True, blank=True)
    description = models.CharField(max_length=500, blank=True)

    def picture_url(self):
        if self.picture_file and hasattr(self.picture_file, 'url'):
            return self.picture_file.url

    def items_count(self):
        # return Item.objects.filter(collection__in=Subquery(Collect.objects.filter(user=self)))
        collects = self.collects.annotate(Count('items'))
        return functools.reduce(lambda a, b: a + b.items__count, collects, 0)
    
    def likes_count(self):
        #return Like.objects.filter(item__collection__user=self).count()

        total_likes = 0
        for collect in self.collects.all():
            for item in collect.items.all():
                total_likes += item.like.count()

        return total_likes

