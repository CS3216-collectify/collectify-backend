from rest_framework import viewsets, permissions, status, exceptions
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
        try:
            serializer.save(user=self.request.user)
        except Exception as err:
            print(err)
            raise exceptions.ValidationError(
                detail="Invalid. Please ensure that you are not already following the same collection",
                code=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def unfollow(self, request, *args, **kwargs):
        collection = self.request.query_params.get('collection')
        if not collection:
            raise exceptions.ParseError()

        self.get_queryset().filter(user=request.user).filter(collection=collection).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
