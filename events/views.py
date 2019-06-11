import locale

from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from django.db.models import Q, Case, When, F
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from events.models import Event, EventCategory
from events.utils import get_event_image
from users.models import UserSwipeAction
from utils.network import parse_request

RELATED_USER_FIELDS = ['related_user__id', 'related_user__user__first_name',
                       'related_user__user_data__fb_profile_image_normal']

EVENTS_PAGE_SIZE = 100;
USER_EVENTS_PAGE_SIZE = 20;


def index(request):
    return HttpResponse("Welcome right Hear :)")


def _events_to_json(request, events, up):
    locale.setlocale(locale.LC_TIME, "he_IL.UTF-8" if up.preferred_language == "he" else "en_US.UTF-8")

    _by_lang = lambda obj, field: (obj.__getattribute__(
        field + '_heb' if up.preferred_language == 'he' else field)) or ''

    events_users = UserSwipeAction.objects.filter(event__in=events, action=UserSwipeAction.ACTION_RIGHT).values_list(
        'event__id', 'user_id')
    users_per_event = {}
    for eu in events_users:
        if eu[0] in users_per_event:
            users_per_event[eu[0]].add(eu[1])
        else:
            users_per_event[eu[0]] = {eu[1]}

    return [{
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
                  'city': _by_lang(event.venue, 'city'), 'distance': int(event.distance.m)},
        'artist': {'firstName': event.artist.first_name, 'lastName': event.artist.last_name,
                   'image': request.build_absolute_uri(
                       event.artist.image.url) if event.artist and event.artist.image else '',
                   'media': [{'type': m.type, 'link': m.link} for m in
                             event.artist.media.all()]} if event.artist else None,
        'media': [{'type': m.type, 'link': m.link, 'youtubeId': m.youtube_id, 'playbackStart': m.playback_start,
                   'playbackEnd': m.playback_end,
                   'thumbnail': request.build_absolute_uri(m.thumbnail.url) if m.thumbnail else ''} for m in
                  event.media.all()],
        'promotion': {'text': event.promotion.get('text', '')} if event.promotion else None,
        'ticketsLink': event.tickets_link,
        'people': list(users_per_event.get(event.id, [])) + [8, 8]

    } for event in events]


@csrf_exempt
@login_required
def get_events(request):
    top_event_id, user_lng, user_lat = parse_request(request, ['topEventId', 'lng', 'lat'])
    up = request.user.userprofile
    ref_location = Point(float(user_lng), float(user_lat), srid=4326)
    valid = Q(title__isnull=False, enabled=True)  # , start_time__gte=timezone.now())
    events = Event.objects.filter(id__gte=318).filter(valid).filter(categories__in=up.preferred_categories.values_list('id', flat=True)).annotate(
        distance=Distance('venue__location', ref_location)).order_by(
        'distance')

    if top_event_id and top_event_id != '-1':
        top_event = Event.objects.filter(id=top_event_id).annotate(
        distance=Distance('venue__location', ref_location))
        events = events.exclude(id=top_event_id)[:EVENTS_PAGE_SIZE - 1]
        events = list(top_event) + list(events)
    else:
        events = events[:EVENTS_PAGE_SIZE]

    events_json = _events_to_json(request, events, up)
    return JsonResponse(events_json, safe=False)


@csrf_exempt
@login_required
def get_user_selected_events(request):
    page, user_lng, user_lat, categories_ids = parse_request(request, ['page', 'lng', 'lat'], ['categoriesIds'])
    page = int(page)
    up = request.user.userprofile

    swipe_right_actions = UserSwipeAction.objects.filter(user=request.user.userprofile,
                                                         action=UserSwipeAction.ACTION_RIGHT)
    selected_events_ids = swipe_right_actions.values_list('event', flat=True)
    ref_location = Point(float(user_lng), float(user_lat), srid=4326)
    selected_events = Event.objects.filter(id__in=selected_events_ids).filter(id__gte=318)
    if categories_ids:
        selected_events = selected_events.filter(categories__in=categories_ids)
    selected_events = selected_events.annotate(
        distance=Distance('venue__location', ref_location)).order_by('distance')
    if categories_ids:
        selected_events = selected_events.filter(categories_ids)
    events_json = _events_to_json(request, selected_events[
                                           page * USER_EVENTS_PAGE_SIZE:(page + 1) * USER_EVENTS_PAGE_SIZE], up)

    return JsonResponse(events_json, safe=False)


@csrf_exempt
@login_required
def get_categories(request):
    up = request.user.userprofile
    is_heb = up.preferred_language == "he"
    categories = EventCategory.objects.filter(enabled=True)

    categories_json = [{
        'id': cat.id,
        'iconName': cat.icon_name,
        'title': cat.title_heb if is_heb else cat.title,
        'image': request.build_absolute_uri(cat.image.url if cat.image else ''),
        'order': cat.order} for cat in categories]

    return JsonResponse(categories_json, safe=False)
