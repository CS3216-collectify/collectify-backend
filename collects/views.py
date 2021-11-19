from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Value, Exists, OuterRef
from django.http import QueryDict
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response

from authentication.authentication import JWTAuthenticationWithoutErrorForSafeMethods
from collectify.permissions import IsOwnerOrReadOnly
from collects.models import Collect, Item, Image
from collects.serializers import CollectionSerializer, CollectionSerializerWithCovers, ImageSerializer, \
    ItemSerializerWithCover, ItemSerializerWithImages
from followers.models import Followers


class CollectionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthenticationWithoutErrorForSafeMethods]

    def get_serializer_class(self):
        if self.action == 'list':
            return CollectionSerializerWithCovers
        else:
            return CollectionSerializer

    def get_queryset(self):
        queryset = Collect.objects.all()
        user = self.request.query_params.get('user')
        category = self.request.query_params.get('category')
        offset = self.request.query_params.get('offset')
        limit = self.request.query_params.get('limit')
        keywords = self.request.query_params.get('keywords')
        is_followed = self.request.query_params.get('followed')

        if keywords is not None:
            vector = SearchVector('collection_name', weight='A') \
                     + SearchVector('collection_description', weight='B') \
                     + SearchVector('category__category_name', weight='C')
            query = SearchQuery(keywords)

            rank = SearchRank(vector, query, normalization=Value(1), cover_density=True)
            queryset1 = queryset.annotate(rank=rank).filter(rank__gte=0.01).order_by('-rank')

            items_search_vector = SearchVector('item_name', 'item_description')
            matched_items = Item.objects.filter(collection__id=OuterRef('id')).annotate(
                search=items_search_vector).filter(search=query)
            queryset2 = queryset.filter(Exists(matched_items)).annotate(rank=Value(0.01))

            queryset = (queryset1 | queryset2).distinct()

        if user is not None:
            queryset = queryset.filter(user__id=user)

        if category is not None:
            queryset = queryset.filter(category_id__id=category)

        if is_followed and self.request.user and self.request.user.is_authenticated:
            if is_followed.lower() == "true":
                queryset = queryset.filter(
                    Exists(Followers.objects.filter(user=self.request.user, collection__id=OuterRef('id')))
                )
            elif is_followed.lower() == "false":
                queryset = queryset.filter(
                    ~Exists(Followers.objects.filter(user=self.request.user, collection__id=OuterRef('id')))
                )

        if offset is not None and limit is not None:
            queryset = queryset[int(offset):int(offset) + int(limit)]

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        super(CollectionViewSet, self).update(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        response = super(CollectionViewSet, self).retrieve(request, *args, **kwargs)

        if self.request.user and self.request.user.is_authenticated and self.get_object().followers.filter(
                user=self.request.user).exists():
            response.data['is_followed'] = True
        else:
            response.data['is_followed'] = False
        return response

    def list(self, request, *args, **kwargs):
        response = super(CollectionViewSet, self).list(request, *args, **kwargs)

        for response_collection in response.data:
            if self.request.user and self.request.user.is_authenticated and \
                    Followers.objects.filter(user=self.request.user).filter(
                        collection=response_collection['collection_id']).exists():
                response_collection['is_followed'] = True
            else:
                response_collection['is_followed'] = False

        return response


class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthenticationWithoutErrorForSafeMethods]

    def get_serializer_class(self):
        if self.action == 'list':
            return ItemSerializerWithCover
        else:
            return ItemSerializerWithImages

    def get_queryset(self):
        offset = self.request.query_params.get('offset')
        limit = self.request.query_params.get('limit')
        collection = self.kwargs.get('collections_pk')

        queryset = Item.objects.filter(collection__id=collection)

        if offset is not None and limit is not None:
            queryset = queryset[int(offset):int(offset) + int(limit)]

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        files = request.FILES.getlist('images')
        for file in files:
            image = Image(image_file=file, item=serializer.instance)
            image.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        collection = self.kwargs.get('collections_pk')
        serializer.save(collection=Collect.objects.get(id=collection))

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        if not request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        deleted_images = []

        # Request data is querydict if it is using multipart form but is dict if json. The check below will help
        # prevent 500 errors
        if isinstance(request.data, QueryDict):
            deleted_images = request.data.getlist('deleted_image_ids')
        elif 'deleted_image_ids' in request.data:
            deleted_images = request.data['deleted_image_ids']

        for image_id in deleted_images:
            Image.objects.get(id=image_id).delete()

        files = request.FILES.getlist('new_images')
        for file in files:
            image = Image(image_file=file, item=serializer.instance)
            image.save()

        if 'updated_collection' in request.data:
            updated_collection_id = request.data['updated_collection']
            if Collect.objects.get(id=updated_collection_id).user == request.user:
                serializer.save(collection=Collect.objects.get(id=updated_collection_id))
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        response = super(ItemViewSet, self).retrieve(request, *args, **kwargs)

        if self.request.user and self.request.user.is_authenticated and self.get_object().like.filter(
                user=self.request.user).exists():
            response.data['is_liked'] = True
        else:
            response.data['is_liked'] = False

        return response


class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
