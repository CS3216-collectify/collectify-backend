from django.urls import path, include
from rest_framework_nested import routers

from .views import CollectionViewSet, ItemViewSet

router = routers.SimpleRouter()
router.register(r'', CollectionViewSet, basename='collections')

collections_router = routers.NestedSimpleRouter(router, r'', lookup='collections')
collections_router.register(r'items', ItemViewSet, basename='collections-items')

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(collections_router.urls)),
]
