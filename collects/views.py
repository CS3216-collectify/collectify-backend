from django.contrib.auth.models import Permission
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response

from authentication.authentication import JWTAuthenticationExcludeSafeMethods
from collects.models import Collect, Item, Image
from collects.serializers import CollectionSerializer, CollectionSerializerWithImages, ImageSerializer, \
    ItemSerializerWithCover, ItemSerializerWithImages
from collectify.permissions import IsOwnerOrReadOnly


class CollectionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthenticationExcludeSafeMethods]

    def get_serializer_class(self):
        if self.action == 'list':
            return CollectionSerializerWithImages
        else:
            return CollectionSerializer

    def get_queryset(self):
        queryset = Collect.objects.all()
        user = self.request.query_params.get('user')
        category = self.request.query_params.get('category')
        offset = self.request.query_params.get('offset')
        limit = self.request.query_params.get('limit')

        if user is not None:
            queryset = queryset.filter(user__id=user)

        if category is not None:
            queryset = queryset.filter(category_id__id=category)

        if offset is not None and limit is not None:
            queryset = queryset[int(offset):int(offset) + int(limit)]

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        super(CollectionViewSet, self).update(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthenticationExcludeSafeMethods]

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
        
        if request.data.get('deleted_image_ids'):
            for image_id in request.data.get('deleted_image_ids'):
                Image.objects.get(id=int(image_id)).delete()
        
        files = request.FILES.getlist('new_images')
        for file in files:
            image = Image(image_file=file, item=serializer.instance)
            image.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
