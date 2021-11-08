from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Exists, OuterRef, Value
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from authentication.authentication import JWTAuthenticationWithoutErrorForSafeMethods
from collectify.permissions import IsOwnerOrReadOnly
from collects.models import Item
from collects.serializers import ItemSerializerWithCover, ItemSerializerWithImages
from followers.models import Followers
from likes.models import Like


class ItemSearchViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthenticationWithoutErrorForSafeMethods]

    def get_serializer_class(self):
        is_detailed = self.request.query_params.get('detailed')
        if is_detailed and is_detailed.lower() == 'true':
            return ItemSerializerWithImages
        return ItemSerializerWithCover

    def get_queryset(self):
        queryset = Item.objects.all()
        keywords = self.request.query_params.get('keywords')
        category = self.request.query_params.get('category')
        is_tradable = self.request.query_params.get('is_tradable')
        is_followed = self.request.query_params.get('followed')
        is_liked = self.request.query_params.get('liked')
        offset = self.request.query_params.get('offset')
        limit = self.request.query_params.get('limit')
        is_discover = self.request.query_params.get('discover')

        if keywords is not None:
            vector = SearchVector('item_name', weight='A') \
                     + SearchVector('item_description', weight='B') \
                     + SearchVector('collection__category__category_name', weight='C') \
                     + SearchVector('collection__collection_name', weight='C') \
                     + SearchVector('collection__collection_description', weight='C')
            query = SearchQuery(keywords)
            rank = SearchRank(vector, query, normalization=Value(1), cover_density=True)
            queryset = queryset.annotate(rank=rank).filter(rank__gte=0.01).order_by('-rank')

        if category is not None:
            queryset = queryset.filter(collection__category__id=category)

        if is_tradable and is_tradable.lower() == "true":
            queryset = queryset.filter(is_tradable=True)
        elif is_tradable and is_tradable.lower() == "false":
            queryset = queryset.filter(is_tradable=False)

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
            if is_discover and is_discover.lower() == "true":
                queryset = queryset.exclude(collection__user=self.request.user)

        if offset is not None and limit is not None:
            queryset = queryset[int(offset):int(offset) + int(limit)]

        return queryset
    
    def list(self, request, *args, **kwargs):
        response = super(ItemSearchViewSet, self).list(request, *args, **kwargs)
        
        if not request.user or not request.user.is_authenticated:
            is_followed = request.query_params.get('followed')
            is_liked = request.query_params.get('liked')
            if is_followed or is_liked:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

        avg_like_count = Like.objects.count()/Item.objects.count()
        popular_threshold = 2 * avg_like_count
        popular_threshold = max(popular_threshold, 2)

        for response_item in response.data:
            if 'likes_count' in response_item: 
                if response_item['likes_count'] >= popular_threshold:
                    response_item['is_popular'] = True
                else:
                    response_item['is_popular'] = False
            else:
                if Item.objects.get(id=response_item['item_id']).likes_count() >= popular_threshold:
                    response_item['is_popular'] = True
                else:
                    response_item['is_popular'] = False

        is_detailed = self.request.query_params.get('detailed')
        
        if not is_detailed or is_detailed.lower() != 'true':
            return response
        
        for response_item in response.data:
            if self.request.user and self.request.user.is_authenticated and \
                    Like.objects.filter(user=self.request.user).filter(item=response_item['item_id']).exists():
                response_item['is_liked'] = True
            else:
                response_item['is_liked'] = False

        return response
