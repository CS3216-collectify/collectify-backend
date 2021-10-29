from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from stream_chat import StreamChat
from collectify.collectifysecrets import STREAM_CHAT_API_SECRET
from collectify.collectifysecrets import STREAM_CHAT_API_KEY

server_client = StreamChat(api_key=STREAM_CHAT_API_KEY, api_secret=STREAM_CHAT_API_SECRET)


class ChatAuth(APIView):
    def post(self, request, format=None):
        data = {
            "chat_id": str(request.user.id),
            "chat_token": server_client.create_token(str(request.user.id))
        }
        return Response(data)
