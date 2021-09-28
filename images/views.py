from django.http import JsonResponse

# Create your views here.

def placeholder(request):
    return JsonResponse({}, content_type = 'application/json')