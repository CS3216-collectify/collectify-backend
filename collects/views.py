from django.http import JsonResponse

# Create your views here.


def get_collections(request):
    return JsonResponse({}, content_type = 'application/json')