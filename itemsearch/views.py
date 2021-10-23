from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from django.db.models import F

from authentication.authentication import JWTAuthenticationExcludeSafeMethods
from authentication.models import User
from collects.models import Item
from likes.models import Like
from followers.models import Followers
from collects.serializers import ItemSerializerWithCover
from collectify.permissions import IsOwnerOrReadOnly

class ItemSearchViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthenticationExcludeSafeMethods]

    def get_serializer_class(self):
        return ItemSerializerWithCover

    def get_queryset(self):
        queryset = Item.objects.all()
        user = self.request.user
        keywords = self.request.query_params.get('keywords')
        followed = self.request.query_params.get('followed')
        liked = self.request.query_params.get('liked')
        offset = self.request.query_params.get('offset')
        limit = self.request.query_params.get('limit')

        if keywords is not None:
            queryset = queryset.filter(item_name__icontains=keywords)

        if user is not None and liked is not None and liked.lower() == 'true':
            #queryset = queryset.filter(Like.objects.filter(item=F('id')).filter(user=user.id).exists())
            pass

        if user is not None and followed is not None and followed.lower() == 'true':
            pass

        if offset is not None and limit is not None:
            queryset = queryset[int(offset):int(offset) + int(limit)]

        return queryset
