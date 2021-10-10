from django.contrib import admin
from .models import Collect, Item, Image

# Register your models here.
admin.site.register(Collect)
admin.site.register(Item)
admin.site.register(Image)