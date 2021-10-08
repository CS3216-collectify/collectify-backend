from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status

from collects.models import Collect
from rest_framework import viewsets
from collects.serializers import CollectionSerializer, CollectionSerializerWithImages


class CollectionViewSet(viewsets.ModelViewSet):

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
