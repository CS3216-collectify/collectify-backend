from django.urls import path

urlpatterns = [
    path('', chat_auth, name='chat_auth'),
]