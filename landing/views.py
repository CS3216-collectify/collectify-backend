from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello. I created this page so that you wouldn't see a 404.")
