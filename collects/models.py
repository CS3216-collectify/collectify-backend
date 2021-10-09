from django.db import models
from categories.models import Category
from authentication.models import User


# Create your models here.

class Collect(models.Model):
    collection_name = models.CharField(max_length=30)
    collection_description = models.CharField(max_length=150, null=True)
    collection_creation = models.DateTimeField(auto_now_add=True)
    category_id = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def cover_images(self):
        return [i.cover_image() for i in self.items.order_by('-item_creation')[:3] if i.cover_image()]


class Item(models.Model):
    item_name = models.CharField(max_length=30)
    item_description = models.TextField()
    item_creation = models.DateTimeField(auto_now_add=True)
    collection_id = models.ForeignKey(Collect, related_name='items', on_delete=models.CASCADE)

    def cover_image(self):
        images = self.images
        if images.exists():
            return images.latest('image_upload').image_url
        else:
            return None
    
    def all_images(self):
        images = self.images.order_by('-image_upload')
        if not images.exists():
            return None
        return None
        #todo


class Image(models.Model):
    image_url = models.URLField()
    image_upload = models.DateTimeField(auto_now_add=True)
    item_id = models.ForeignKey(Item, related_name='images', on_delete=models.CASCADE)
