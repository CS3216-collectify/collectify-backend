from django.db import models
from categories.models import Category
from django.contrib.auth.models import User


# Create your models here.

class Collects(models.Model):
    collection_name = models.CharField(max_length=30)
    collection_description = models.CharField(max_length=150)
    collection_creation = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
