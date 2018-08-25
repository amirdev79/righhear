from django.http import HttpResponse, JsonResponse

from events.models import Event


def index(request):
    return HttpResponse("Welcome right Hear :)")


def get_events(request):
    # return HttpResponse("Get Events :)")
    events = [{
                  'id': event.id,
                  'title': event.title,
                  'createdBy': {'firstName': event.created_by.user.first_name,
                                'lastName': event.created_by.user.last_name},
                  'category': {'title': event.category.title,
                               'image': event.category.image.url if event.category.image else ''},
                  'subCategory': {'title': event.sub_category.title,
                                  'image': event.sub_category.image.url if event.sub_category.image else ''},
                  'shortDescription': event.description,
                  'description': event.description,
                  'price': event.price,
                  'startTime': event.start_time.strftime("%d.%m at %H:%M"),
                  'endTime': event.end_time.strftime("%d.%m - %H:%M"),
                  'venue': {'name': event.venue.name, 'streetAddress': event.venue.street_address,
                            'city': event.venue.city},
                  'artist': {'firstName': event.artist.first_name, 'lastName': event.artist.lastName,
                             'image': event.artist.image.url,
                             'media': [{'type': m.type, 'link': m.link} for m in
                                       event.artist.media.all()]} if event.artist else None,
                  'media': [{'type': m.type, 'link': m.link} for m in event.media.all()]

              } for event in Event.objects.all()]
    return JsonResponse(events, safe=False)
