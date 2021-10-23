from django.urls import path

from itemsearch.views import ItemSearchViewSet

item_search_list = ItemSearchViewSet.as_view({
    'get': 'list',
})

urlpatterns = [
    path('', item_search_list, name='item_search_list'),
]