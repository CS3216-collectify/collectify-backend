from django.urls import path
from .views import ChatAuth

from chat.views import ChatAuth

urlpatterns = [
    path('', ChatAuth.as_view(), name='chat_auth'),
]