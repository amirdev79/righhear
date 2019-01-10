from django.db.models import Q
from django.http import HttpResponse, JsonResponse

from events.models import Event
from events.utils import get_event_image


def index(request):
    return HttpResponse("Welcome right Hear :)")


def get_events(request):

    up = request.user.userprofile

    _by_lang = lambda obj, field : (obj.__getattribute__(field + '_heb' if up.preferred_language == 'he' else field)) or ''

    valid = Q(title__isnull=False, enabled=True)#, start_time__gte=timezone.now())
    events = Event.objects.filter(valid)

    events = [{
                  'id': event.id,
                  'title': _by_lang(event, 'title'),
                  'createdBy': {'firstName': event.created_by.user.first_name,
                                'lastName': event.created_by.user.last_name},
                  'categories': [{'title': _by_lang(c, 'title'),
                                  'image': c.image.url if c.image else ''} for c in event.categories.all()],
                  'subCategories': [{'title': _by_lang(s, 'title'),
                                  'image': s.image.url if s.image else ''} for s in event.sub_categories.all()],
                  'shortDescription': _by_lang(event, 'short_description'),
                  'description': _by_lang(event, 'description'),
                  'price': event.price,
                  'startTime': event.start_time.strftime("%b %d, %H:%M") if event.start_time else '',
                  'endTime': event.end_time.strftime("%d.%m - %H:%M") if event.end_time else '',
                  'image': get_event_image(request, event),
                  'venue': {'name': _by_lang(event.venue, 'name'), 'streetAddress': _by_lang(event.venue, 'street_address'),
                            'city': _by_lang(event.venue, 'city'), 'lat': event.venue.latitude, 'lng': event.venue.longitude},
                  'artist': {'firstName': event.artist.first_name, 'lastName': event.artist.last_name,
                             'image': request.build_absolute_uri(event.artist.image.url),
                             'media': [{'type': m.type, 'link': m.link} for m in
                                       event.artist.media.all()]} if event.artist else None,
                  'media': [{'type': m.type, 'link': m.link, 'thumbnail': request.build_absolute_uri(m.thumbnail.url) if m.thumbnail else ''} for m in event.media.all()],
                  'promotion': {'text': event.promotion.get('text', '')} if event.promotion else None,

              } for event in events]
    return JsonResponse(events, safe=False)
