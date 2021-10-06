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


class Item(models.Model):
    item_name = models.CharField(max_length=30)
    item_description = models.TextField()
    item_creation = models.DateTimeField(auto_now_add=True)
    collection_id = models.ForeignKey(Collect, on_delete=models.CASCADE)


class Image(models.Model):
    image_url = models.TextField()
    image_upload = models.DateTimeField(auto_now_add=True)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
