from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from authentication.authentication import JWTAuthenticationExcludeSafeMethods
from collectify.permissions import IsOwnerOrReadOnly
from followers.models import Followers
from followers.serializers import FollowerSerializer


class FollowerViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthenticationExcludeSafeMethods]
    serializer_class = FollowerSerializer

    def get_queryset(self):
        queryset = Followers.objects.all()
        collection_id = self.request.query_params.get('collection')
        offset = self.request.query_params.get('offset')
        limit = self.request.query_params.get('limit')

        if collection_id is not None:
            queryset = queryset.filter(collection__id=collection_id)

        if offset is not None and limit is not None:
            queryset = queryset[int(offset):int(offset) + int(limit)]

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def unfollow(self, request, *args, **kwargs):
        self.get_queryset().filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

