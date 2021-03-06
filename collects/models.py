import os.path
import traceback
from io import BytesIO

import PIL.Image
from PIL import ImageOps
from django.core.files.base import ContentFile
from django.db import models

from authentication.models import User
from categories.models import Category

THUMB_SIZE = 512, 512


# Create your models here.


class Collect(models.Model):
    collection_name = models.CharField(max_length=70)
    collection_description = models.CharField(max_length=150, blank=True)
    collection_creation = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category,
        related_name="collects",
        on_delete=models.SET_NULL,
        null=True
    )
    user = models.ForeignKey(User, related_name='collects', on_delete=models.CASCADE)

    def cover_images(self):
        return [i.cover_image() for i in self.items.order_by('-item_creation')[:3] if i.cover_image()]

    def __str__(self):
        return self.collection_name

    def items_count(self):
        return self.items.count()

    class Meta:
        ordering = ["-collection_creation"]


class Item(models.Model):
    item_name = models.CharField(max_length=70)
    item_description = models.TextField(blank=True)
    item_creation = models.DateTimeField(auto_now_add=True)
    collection = models.ForeignKey(Collect, related_name='items', on_delete=models.CASCADE)
    is_tradable = models.BooleanField(default=False)

    def user(self):
        return self.collection.user

    def cover_image(self):
        images = self.images
        if images.exists():
            image = images.earliest('image_upload')
            if image.thumbnail_file:
                return image.thumbnail_file.url
            else:
                return image.image_file.url
        else:
            return None

    def likes_count(self):
        return self.like.count()

    def __str__(self):
        return self.item_name

    class Meta:
        ordering = ['-item_creation']


class Image(models.Model):
    image_file = models.ImageField(upload_to='item_images', null=True)
    thumbnail_file = models.ImageField(upload_to='item_thumbnail', null=True)
    image_upload = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(Item, related_name='images', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        try:
            if 'update_fields' not in kwargs or 'image_file' in kwargs['update_fields']:
                print('Generating thumbnails from image')
                if not self.make_thumbnail():
                    print('Could not create thumbnail. Please check file format')

        except Exception as err:
            print(err)
            print(traceback.format_exc())
            print('Could not save thumbnail')

        super().save(*args, **kwargs)

    def make_thumbnail(self):
        with PIL.Image.open(self.image_file) as image:
            src_extension = None
            if image.format:
                print('inferred file format: ' + image.format)
                src_extension = '.' + image.format
            image = ImageOps.exif_transpose(image)

            image.thumbnail(THUMB_SIZE, PIL.Image.ANTIALIAS)
            thumb_name, thumb_extension = os.path.splitext(self.image_file.name)

            if not thumb_extension and src_extension:
                thumb_extension = src_extension

            thumb_extension = thumb_extension.lower()
            thumb_filename = thumb_name + '_thumb' + thumb_extension
            print('Creating thumbnail with name: ' + thumb_filename)

            if thumb_extension in ['.jpg', '.jpeg', '.jfif']:
                file_type = 'JPEG'
            elif thumb_extension == '.gif':
                file_type = 'GIF'
            elif thumb_extension == '.png':
                file_type = 'PNG'
            else:
                print(f"Unknown thumb extension {thumb_extension}. Skipping.")
                return False  # Unrecognized file type

            # Save thumbnail to in-memory file
            temp_thumb = BytesIO()
            image.save(temp_thumb, file_type)
            temp_thumb.seek(0)

            # set save=False, otherwise it will run in an infinite loop
            try:
                self.thumbnail_file.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
            except Exception as err:
                print(err)
                print('Django is unable to save thumbnail')

            temp_thumb.close()
            print('Thumbnail generated successfully')
            return True

    def user(self):
        return self.item.collection.user

    def __str__(self):
        return self.item.item_name + ' image'

    class Meta:
        ordering = ['image_upload']
