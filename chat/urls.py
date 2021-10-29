from django.urls import path

from chat.views import ChatAuth

urlpatterns = [
    path('', ChatAuth.as_view(), name='chat_auth'),
]