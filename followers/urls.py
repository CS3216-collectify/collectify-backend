from django.urls import path

from followers.views import FollowerViewSet

follower_list = FollowerViewSet.as_view({
    'get': 'list',
    'post': 'create',
    'delete': 'unfollow'
})

urlpatterns = [
    path('', follower_list, name='follower_list'),
]
