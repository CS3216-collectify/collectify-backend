from rest_framework import generics
from rest_framework import mixins, permissions

from categories.models import Category
from categories.serializers import CategorySerializer
from collects.models import Collect


class CategoryList(mixins.ListModelMixin,
                   generics.GenericAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def get(self, request, *args, **kwargs):
        response = self.list(request, *args, **kwargs)
        indicate_empty = request.query_params.get('indicateEmpty')

        if not indicate_empty or indicate_empty.lower() != 'true':
            return response

        for response_category in response.data:
            total_items = 0
            category_collections = Collect.objects.filter(category_id=response_category['category_id'])

            for collection in category_collections:
                total_items += collection.items_count()

            if total_items > 0:
                response_category['is_empty'] = False
            else:
                response_category['is_empty'] = True

        response.data.sort(key=lambda x: x['is_empty'])
        return response
