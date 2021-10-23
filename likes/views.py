from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.response import Response

from authentication.authentication import JWTAuthenticationExcludeSafeMethods
from collectify.permissions import IsOwnerOrReadOnly
from likes.models import Like
from likes.serializers import LikeSerializer


class LikeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthenticationExcludeSafeMethods]
    serializer_class = LikeSerializer

    def get_queryset(self):
        queryset = Like.objects.all()
        item = self.request.query_params.get('item')
        offset = self.request.query_params.get('offset')
        limit = self.request.query_params.get('limit')

        if item is not None:
            queryset = queryset.filter(item__id=item)

        if offset is not None and limit is not None:
            queryset = queryset[int(offset):int(offset) + int(limit)]

        return queryset

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as err:
            print(err)
            raise exceptions.ValidationError(
                detail="Invalid. Item has already been liked by user",
                code=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def unlike(self, request, *args, **kwargs):
        item = self.request.query_params.get('item')
        if not item:
            raise exceptions.ParseError()

        self.get_queryset().filter(user=request.user).filter(item=item).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
