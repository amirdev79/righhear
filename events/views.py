from django.http import HttpResponse, JsonResponse

def index(request):
    return HttpResponse("Welcome right Hear :)")

def get_events(request):

    return JsonResponse()