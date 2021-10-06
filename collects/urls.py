from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

# TODO: replace with router when list is implemented
collection_detail = views.CollectionViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

collection_list = views.CollectionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

urlpatterns = format_suffix_patterns([
    path('', collection_list, name='collection-list'),
    path('<int:pk>', collection_detail, name='collection-detail'),
])
