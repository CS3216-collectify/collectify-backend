from rest_framework import serializers

from collects.models import Item
from .models import Like


class LikeSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.CharField(source='user.id', read_only=True)
    profile_picture_url = serializers.URLField(source='user.picture_url', read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(),
        source='item',
        write_only=True
    )

    class Meta:
        model = Like
        fields = ['username', 'user_id', 'profile_picture_url', 'item_id']
