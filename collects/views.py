from django.contrib.auth.models import Permission
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response

from collects.models import Collect, Item
from collects.serializers import CollectionSerializer, CollectionSerializerWithImages, ItemSerializerWithCover, \
    ItemSerializerWithImages
from collectify.permissions import IsOwnerOrReadOnly


class CollectionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

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


# explore drf-nested-routers
class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return ItemSerializerWithCover
        else:
            return ItemSerializerWithImages

    def get_queryset(self):
        queryset = Item.objects.all()
        offset = self.request.query_params.get('offset')
        limit = self.request.query_params.get('limit')
        collect_pk = self.kwargs.get('collect_pk')

        if collect_pk:
            queryset = Item.objects.filter(collect=collect_pk)

        if offset is not None and limit is not None:
            queryset = queryset[int(offset):int(offset) + int(limit)]

    def update(self, request, *args, **kwargs):
        super(CollectionViewSet, self).update(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)
