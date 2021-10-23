from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Exists, OuterRef, Value
from rest_framework import viewsets, permissions

from authentication.authentication import JWTAuthenticationWithoutErrorForSafeMethods
from collectify.permissions import IsOwnerOrReadOnly
from collects.models import Item
from collects.serializers import ItemSerializerWithCover
from followers.models import Followers
from likes.models import Like


class ItemSearchViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthenticationWithoutErrorForSafeMethods]

    def get_serializer_class(self):
        return ItemSerializerWithCover

    def get_queryset(self):
        queryset = Item.objects.all()
        keywords = self.request.query_params.get('keywords')
        is_followed = self.request.query_params.get('followed')
        is_liked = self.request.query_params.get('liked')
        offset = self.request.query_params.get('offset')
        limit = self.request.query_params.get('limit')

        if keywords is not None:
            vector = SearchVector('item_name', weight='A') \
                     + SearchVector('item_description', weight='B')
            query = SearchQuery(keywords)
            rank = SearchRank(vector, query, normalization=Value(1), cover_density=True)
            queryset = queryset.annotate(rank=rank).filter(rank__gte=0.1).order_by('-rank')

        if self.request.user and self.request.user.is_authenticated:
            if is_followed and is_followed.lower() == "true":
                queryset = queryset.filter(
                    Exists(Followers.objects.filter(user=self.request.user, collection__id=OuterRef('collection_id')))
                )
            elif is_followed and is_followed.lower() == "false":
                queryset = queryset.filter(
                    ~Exists(Followers.objects.filter(user=self.request.user, collection__id=OuterRef('collection_id')))
                )
            if is_liked and is_liked.lower() == "true":
                queryset = queryset.filter(
                    Exists(Like.objects.filter(user=self.request.user, item__id=OuterRef('id')))
                )
            elif is_liked and is_liked.lower() == "false":
                queryset = queryset.filter(
                    ~Exists(Like.objects.filter(user=self.request.user, item__id=OuterRef('id')))
                )

        if offset is not None and limit is not None:
            queryset = queryset[int(offset):int(offset) + int(limit)]

        return queryset
