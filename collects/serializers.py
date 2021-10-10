from rest_framework import serializers

from categories.models import Category
from collects.models import Collect, Item, Image


class CollectionSerializer(serializers.ModelSerializer):
    collection_id = serializers.ReadOnlyField(source='id')
    collection_name = serializers.CharField(max_length=30)
    collection_description = serializers.CharField(max_length=150)
    collection_creation_date = serializers.DateTimeField(source='collection_creation', read_only=True)
    user_id = serializers.ReadOnlyField(source='user.id')
    category_id = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Category.objects.all(), source='category')
    category_name = serializers.ReadOnlyField(read_only=True, source='category.category_name')

    class Meta:
        model = Collect
        fields = ('collection_id', 'collection_name', 'collection_description', 'collection_creation_date',
                  'user_id', 'category_id', 'category_name')


class CollectionSerializerWithImages(CollectionSerializer):
    cover_images = serializers.ListField(allow_empty=True, read_only=True)

    class Meta:
        model = Collect
        fields = ('collection_id', 'collection_name', 'collection_description', 'collection_creation_date',
                  'user_id', 'category_id', 'category_name', 'cover_images')


class ImageSerializer(serializers.ModelSerializer):
    image_id = serializers.ReadOnlyField(source='id')
    image_url = serializers.URLField(read_only=True)
    image_upload_date = serializers.DateTimeField(source='image_upload', read_only=True)
    class Meta:
        model = Image
        fields = ['image_id', 'image_url', 'image_upload_date']


class ItemSerializer(serializers.ModelSerializer):
    item_id = serializers.ReadOnlyField(source='id')
    item_name = serializers.CharField(max_length=30)
    item_description = serializers.CharField()
    item_creation_date = serializers.DateTimeField(source='item_creation', read_only=True)
    class Meta:
        model = Item
        fields = ['item_id', 'item_name', 'item_description', 'item_creation_date']


class ItemSerializerWithCover(ItemSerializer):
    cover_image = serializers.URLField(read_only=True)
    class Meta:
        model = Item
        fields = ['item_id', 'item_name', 'item_description', 'item_creation_date', 'cover_image']


class ItemSerializerWithImages(ItemSerializer):
    images = ImageSerializer(many=True, read_only=True)
    class Meta:
        model = Item
        fields = ['item_id', 'item_name', 'item_description', 'item_creation_date', 'images']
