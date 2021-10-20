from django.urls import path

from likes.views import LikeViewSet

like_list = LikeViewSet.as_view({
    'get': 'list',
    'post': 'create',
    'delete': 'unlike'
})

urlpatterns = [
    path('', like_list, name='like_list'),
]