from django.db import models
from categories.models import Category
from authentication.models import User


# Create your models here.

class Collect(models.Model):
    collection_name = models.CharField(max_length=30)
    collection_description = models.CharField(max_length=150, null=True)
    collection_creation = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category,
        related_name="collects",
        on_delete=models.SET_NULL,
        null=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def cover_images(self):
        return [i.cover_image() for i in self.items.order_by('-item_creation')[:3] if i.cover_image()]
    
    def __str__(self):
        return self.collection_name


class Item(models.Model):
    item_name = models.CharField(max_length=30)
    item_description = models.TextField()
    item_creation = models.DateTimeField(auto_now_add=True)
    collection = models.ForeignKey(Collect, related_name='items', on_delete=models.CASCADE)

    def user(self):
        return self.collection.user

    def cover_image(self):
        images = self.images
        if images.exists():
            return images.latest('image_upload').image_file.url
        else:
            return None
    
    def __str__(self):
        return self.item_name


class Image(models.Model):
    image_file = models.ImageField(upload_to='item_images', null=True)
    image_upload = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(Item, related_name='images', on_delete=models.CASCADE)

    def user(self):
        return self.item.collection.user

    def __str__(self):
        return self.item.item_name + ' image'
