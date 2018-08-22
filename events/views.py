from django.http import HttpResponse, JsonResponse

from events.models import Event
from utils.network import values_to_camelcase


def index(request):
    return HttpResponse("Welcome right Hear :)")


def get_events(request):
    # return HttpResponse("Get Events :)")
    events = [{
                  'id': event.id,
                  'title': event.title,
                  'createdBy': {'firstName': event.created_by.user.first_name,
                                'lastName': event.created_by.user.last_name},
                  'cateogry': {'title': event.category.title,
                               'image': event.category.image.url if event.category.image else ''},
                  'subCateogry': {'title': event.sub_category.title,
                                  'image': event.sub_category.image.url if event.sub_category.image else ''},
                  'shortDescription': event.description,
                  'price': event.price,
                  'startTime': event.start_time,
                  'endTime': event.end_time,
                  'venue': {'name': event.venue.name, 'streetAddress': event.venue.street_address,
                            'city': event.venue.city},
                  'media': [{'type': m.type, 'link': m.link} for m in event.media.all()]

              } for event in Event.objects.all()]
    return JsonResponse(events, safe=False)
