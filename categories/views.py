from categories.models import Category
from categories.serializers import CategorySerializer
from rest_framework import mixins
from rest_framework import generics


class CategoryList(mixins.ListModelMixin,
                   generics.GenericAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
