from rest_framework import serializers

from categories.models import Category


class CategorySerializer(serializers.ModelSerializer):
    category_id = serializers.ReadOnlyField(source='id')
    name = serializers.CharField(max_length=30, source='category_name')

    class Meta:
        model = Category
        fields = ('category_id', 'name')
