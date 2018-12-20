from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from events.models import Event


def index(request):
    return HttpResponse("Welcome right Hear :)")


def get_events(request):

    valid = Q(title__isnull=False, artist__image__isnull=False, enabled=True, start_time__gte=timezone.now())
    events = Event.objects.filter(valid)

    events = [{
                  'id': event.id,
                  'title': event.title,
                  'createdBy': {'firstName': event.created_by.user.first_name,
                                'lastName': event.created_by.user.last_name},
                  'category': {'title': event.category.title,
                               'image': event.category.image.url if event.category.image else ''},
                  'subCategories': [{'title': s.title,
                                  'image': s.image.url if s.image else ''} for s in event.sub_categories.all()],
                  'shortDescription': event.short_description,
                  'description': event.description,
                  'price': event.price,
                  'startTime': event.start_time.strftime("%b %d, %H:%M"),
                  'endTime': event.end_time.strftime("%d.%m - %H:%M"),
                  'venue': {'name': event.venue.name, 'streetAddress': event.venue.street_address,
                            'city': event.venue.city, 'lat': event.venue.latitude, 'lng': event.venue.longitude},
                  'artist': {'firstName': event.artist.first_name, 'lastName': event.artist.last_name,
                             'image': request.build_absolute_uri(event.artist.image.url),
                             'media': [{'type': m.type, 'link': m.link} for m in
                                       event.artist.media.all()]} if event.artist else None,
                  'media': [{'type': m.type, 'link': m.link, 'thumbnail': request.build_absolute_uri(m.thumbnail.url) if m.thumbnail else ''} for m in event.media.all()],
                  'promotion': {'text': event.promotion.get('text', '')} if event.promotion else None,

              } for event in events]
    return JsonResponse(events, safe=False)
