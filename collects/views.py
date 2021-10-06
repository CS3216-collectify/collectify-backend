from django.http import JsonResponse
from collects.models import Collect
from rest_framework import viewsets
from collects.serializers import CollectionSerializer


def get_collections(request):
    return JsonResponse({}, content_type='application/json')


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collect.objects.all()
    serializer_class = CollectionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
