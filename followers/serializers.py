from rest_framework import serializers

from authentication.models import User
from collects.models import Collect
from followers.models import Followers


class FollowerSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')
    profile_picture_url = serializers.URLField(source='user.picture_url', read_only=True)
    collection_id = serializers.PrimaryKeyRelatedField(
        queryset=Collect.objects.all(),
        source='collection',
        write_only=True
    )

    class Meta:
        model = Followers
        fields = ('username', 'user_id', 'profile_picture_url', 'collection_id')
