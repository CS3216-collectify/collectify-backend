from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.CollectionViewSet, 'collections')
router.register(r'collections/<int:pk>', views.ItemViewSet, 'items')

urlpatterns = [
    path('', include(router.urls)),
]
