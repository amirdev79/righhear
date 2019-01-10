import datetime
import json
import re
import tempfile

import requests
from django.core.files.images import ImageFile
from django.core.mail import EmailMessage
from django.db.models import DateTimeField, CharField
from django.db.models.functions import Cast, TruncSecond

from events.models import Venue, Event, EventCategory
from events.utils import get_gmaps_info
from righthear import settings
from users.models import UserProfile

EASY_CATEGORIES = {'music': 5818, 'bars': 424, 'theater': 12877, 'standup': 12879}
now = datetime.datetime.now()
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
easy_scraper_user = UserProfile.objects.get(user__username=settings.EASY_CO_IL_USERNAME)
music_category = EventCategory.objects.get(id=0)
bars_category = EventCategory.objects.get(id=14)
music_event_default_image = ImageFile(open("static/images/events/categories_defauls/music_default.jpg", "rb"))
bars_event_default_image = ImageFile(open("static/images/events/categories_defauls/bars_default.jpeg", "rb"))

DEFAULTS_FOR_SCRAPER = {'title': '',
                        'description': '',
                        'scraper_username': settings.EASY_CO_IL_USERNAME,
                        'sub_categories': '',
                        'short_description': '',
                        'short_description_heb': '',
                        'description': '',
                        'description_heb': '',
                        'image_url': '',
                        'venue_link': '',
                        'end_time': '',
                        'categories': '',
                        'audiences': ''
                        }

CSV_FIELDS = [
    'scraper_username', 'title', 'title_heb', 'start_time', 'end_time', 'categories', 'sub_categories', 'audiences',
    'short_description', 'short_description_heb', 'description', 'description_heb', 'price', 'image_url', 'venue_name',
    'venue_street_address', 'venue_city', 'venue_phone_number', 'venue_lng', 'venue_lat', 'venue_link']


# easy
def _parse_theater_event(event_json):
    title = event_json['bizname'][::-1]
    _date, _time = None, None
    _datetime = event_json['openhours'].replace(' ב-', '|')
    _datetime_arr = _datetime.split('|')
    if len(_datetime_arr) == 2:
        if _datetime_arr[0] == 'היום':
            _datetime = '%s/%s/%s' % (now.day, now.month, now.year) + '|' + _datetime_arr[1]
        elif _datetime_arr[0] == 'מחר':
            _datetime = '%s/%s/%s' % (tomorrow.day, tomorrow.month, tomorrow.year) + '|' + _datetime_arr[1]
        elif _datetime_arr[0].count('/') == 1:
            _datetime = _datetime_arr[0] + '/' + str(now.year) + '|' + _datetime_arr[1]

        start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y|%H:%M').astimezone()
    else:
        if _datetime.count('/') == 1:
            _datetime += '/' + str(now.year)
        start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y').astimezone()

    return {'title': title, 'start_time': start_time}


def _parse_standup_event(event_json):
    title = event_json['bizname'][::-1]
    _date, _time = None, None
    _datetime = event_json['openhours'].replace(' ב-', '|')
    _datetime_arr = _datetime.split('|')
    if len(_datetime_arr) == 2:
        if _datetime_arr[0] == 'היום':
            _datetime = '%s/%s/%s' % (now.day, now.month, now.year) + '|' + _datetime_arr[1]
        elif _datetime_arr[0] == 'מחר':
            _datetime = '%s/%s/%s' % (tomorrow.day, tomorrow.month, tomorrow.year) + '|' + _datetime_arr[1]
        elif _datetime_arr[0].count('/') == 1:
            _datetime = _datetime_arr[0] + '/' + str(now.year) + '|' + _datetime_arr[1]

        start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y|%H:%M')
    else:
        start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y')

    return {'title': title, 'start_time': start_time}


def _to_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%d.%m.%y, %H:%M').astimezone()


def events_to_csv():
    events = get_events('music') + get_events('standup')

    existing_events_cmp_fields = Event.objects.filter(start_time__gte=datetime.datetime.now()).annotate(
        start_time_str=Cast(TruncSecond('start_time', DateTimeField()), CharField())).values_list('title_heb',
                                                                                                  'start_time_str')
    csv_file = tempfile.NamedTemporaryFile(suffix='.csv')
    with open(csv_file.name, 'w+') as f:

        lines = [','.join(CSV_FIELDS)]
        for i, event_json in enumerate(events):
            print('doing event ' + str(i))
            parsed = _parse_event(event_json)
            parsed.update(DEFAULTS_FOR_SCRAPER)

            event_start_datetime = _to_datetime(parsed.get('start_time'))
            db_format_datetime = event_start_datetime.strftime('%Y-%m-%d %H:%M:%S')
            event_cmp_fields = parsed.get('title_heb'), db_format_datetime
            if event_cmp_fields in existing_events_cmp_fields:
                print('event %s - %s is already in DB. excluding from csv...' % (
                    event_cmp_fields[0], event_cmp_fields[1]))
            elif event_start_datetime < datetime.datetime.now().astimezone():
                print('event %s - %s-%s time has passed. excluding from csv...' % (
                    event_cmp_fields[0], parsed.get('start_time'), parsed.get('end_time')))
            else:
                lines.append(','.join(['"' + parsed.get(field, '').replace('"', '""') + '"' for field in CSV_FIELDS]))
        f.write('\n'.join(lines))

        print('csv created. sending by email...')

        email = EmailMessage(
            'Easy.co.il Events scraper',
            'See attached CSV. please update the fields: title, description, short description (non hebrew ones)\nDo not touch the venue fields!',
            'righthearil@gmail.com',
            ['righthearil@gmail.com'],
        )

        email.attach_file(csv_file.name)
        email.send()


# def scrape_easy(category):
#     events_list = get_events(category)
#
#     new_music_events, new_music_venues, new_bars_events, new_bars_venues = [], [], [], []
#     total_music_events, total_bars_events = 0, 0
#     if category == 'music':
#         for event in events_list:
#             total_music_events += 1
#             event, event_created, venue, venue_created = _parse_music_event(event)
#             if event_created:
#                 new_music_events.append(event)
#             if venue_created:
#                 new_music_venues.append(venue)
#         print('%d new music events added of total %d\n-------------------------------------------- %s' % (
#             len(new_music_events), total_music_events, '\n'.join([str(e) for e in new_music_events])))
#         print('%d new music venues added of total %d:\n------------------------------------------- %s' % (
#             len(new_music_venues), total_music_events, '\n'.join([str(v) for v in new_music_venues])))
#
#     elif category == 'bars':
#         for event in events_list:
#             total_bars_events += 1
#             event, event_created, venue, venue_created = _parse_bars_event(event)
#             if event_created:
#                 new_bars_events.append(event)
#             if venue_created:
#                 new_bars_venues.append(venue)
#
#         print('%d new bars events added of total %d\n-------------------------------------------- %s' % (
#             len(new_bars_events), total_bars_events, '\n'.join([str(e) for e in new_bars_events])))
#         print('%d new bars venues added of total %d:\n------------------------------------------- %s' % (
#             len(new_bars_venues), total_bars_events, '\n'.join([str(v) for v in new_bars_venues])))
#
#     elif category == 'theater':
#         events = [_parse_theater_event(event) for event in events_list]
#     elif category == 'standup':
#         events = [_parse_standup_event(event) for event in events_list]
#     else:
#         events = []


def get_events(category):
    events_list = []
    current_page = 0
    print('working..')
    while current_page == 0 or json_list.get('nextpage'):
        url = 'https://easy.co.il/json/list.json?c=' + str(EASY_CATEGORIES.get(category))
        if current_page > 0:
            url += '&listpage=' + str(current_page)
        response = requests.get(url)
        print('url: ' + 'https://easy.co.il/json/list.json?c=%d&listpage=%s' % (
            EASY_CATEGORIES.get(category), str(current_page) if current_page > 0 else ''))
        json_list = json.loads(response.content).get('bizlist')
        events_list += json_list.get('list')
        current_page += 1

    return events_list


def _get_start_time(event_json):
    # get datetime
    _date, _time = None, None
    _datetime = event_json['openhours'].replace(' ב-', '|')
    _datetime_arr = _datetime.split('|')
    if len(_datetime_arr) == 2:
        if _datetime_arr[0] == 'היום':
            _datetime = '%s/%s/%s' % (now.day, now.month, now.year) + '|' + _datetime_arr[1]
        elif _datetime_arr[0] == 'מחר':
            _datetime = '%s/%s/%s' % (tomorrow.day, tomorrow.month, tomorrow.year) + '|' + _datetime_arr[1]
        elif _datetime_arr[0].count('/') == 1:
            _datetime = _datetime_arr[0] + '/' + str(now.year) + '|' + _datetime_arr[1]

        start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y|%H:%M').astimezone()
    elif _datetime.count('/') == 1:
        start_time = datetime.datetime.strptime(_datetime + '/' + str(now.year), '%d/%m/%Y').astimezone()
    else:
        start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y').astimezone()

    return start_time.strftime('%d.%m.%y, %H:%M')


def _get_price(event_json):
    prop = event_json.get('prop')
    if prop and 'title' in prop[0] and '₪' in prop[0]['title']:
        return re.sub('[^0-9]', '', prop[0]['title'])
    else:
        return ''


def _parse_event(event_json):
    event = {'title_heb': event_json['bizname'], 'start_time': _get_start_time(event_json)}
    venue_name, city = event_json.get('address').split(',')
    event['venue_name'] = venue_name
    event['venue_city'] = city
    gmaps_address = get_gmaps_info(venue_name)
    event['venue_street_address'] = gmaps_address['formatted_address'] if gmaps_address else None
    event['venue_lng'] = str(gmaps_address['lng']) if gmaps_address else '0'
    event['venue_lat'] = str(gmaps_address['lat']) if gmaps_address else '0'
    event['venue_phone_number'] = event_json.get('phone')
    event['price'] = _get_price(event_json)
    return event


# def _parse_music_event(event_json):
#     # get title
#     title = event_json['bizname']
#
#     # get datetime
#     _date, _time = None, None
#     _datetime = event_json['openhours'].replace(' ב-', '|')
#     _datetime_arr = _datetime.split('|')
#     if len(_datetime_arr) == 2:
#         if _datetime_arr[0] == 'היום':
#             _datetime = '%s/%s/%s' % (now.day, now.month, now.year) + '|' + _datetime_arr[1]
#         elif _datetime_arr[0] == 'מחר':
#             _datetime = '%s/%s/%s' % (tomorrow.day, tomorrow.month, tomorrow.year) + '|' + _datetime_arr[1]
#         elif _datetime_arr[0].count('/') == 1:
#             _datetime = _datetime_arr[0] + '/' + str(now.year) + '|' + _datetime_arr[1]
#
#         start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y|%H:%M')
#     else:
#         start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y')
#
#     # get venue
#     venue_name, city = event_json.get('address').split(',')
#     venue, venue_created = Venue.objects.get_or_create(name=venue_name)
#
#     if venue_created:
#         print('venue created: ' + venue_name + ',city: ' + city)
#
#         venue.city = city
#         gmaps_address = get_gmaps_info(venue_name)
#         venue.street_address = gmaps_address['formatted_address']
#         venue.longitude, venue.latitude = event_json.get('lng'), event_json.get('lat')
#         venue.phone_number = event_json.get('phone')
#         venue.save()
#
#     # get price
#     price = None
#     prop = event_json.get('prop')
#     if prop and 'title' in prop[0] and '₪' in prop[0]['title']:
#         price = int(re.sub('[^0-9]', '', prop[0]['title']))
#
#     # create event
#     defaults = {'venue': venue, 'price': price, 'created_by': easy_scraper_user}
#     event, event_created = Event.objects.get_or_create(title=title, start_time=start_time,
#                                                        defaults=defaults)
#     if event_created:
#         event.image = music_event_default_image
#         event.categories.add(music_category)
#         event.save()
#         print('event created: ' + str(event))
#
#     return event, event_created, venue, venue_created


# def _parse_bars_event(event_json):
#     title = event_json['bizname']
#     _date, _time = None, None
#     if not 'openhours' in event_json:
#         start_time = None
#     else:
#         _datetime = event_json['openhours'].replace(' ב-', '|')
#         _datetime_arr = _datetime.split('|')
#         if len(_datetime_arr) == 2:
#             if _datetime_arr[0] == 'היום':
#                 _datetime = '%s/%s/%s' % (now.day, now.month, now.year) + '|' + _datetime_arr[1]
#             elif _datetime_arr[0] == 'מחר':
#                 _datetime = '%s/%s/%s' % (tomorrow.day, tomorrow.month, tomorrow.year) + '|' + _datetime_arr[1]
#             elif _datetime_arr[0].count('/') == 1:
#                 _datetime = _datetime_arr[0] + '/' + str(now.year) + '|' + _datetime_arr[1]
#
#             start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y|%H:%M')
#         elif _datetime in ['סגור', 'פתוח']:
#             start_time = None
#         else:
#             start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y')
#
#     # get venue
#     address_arr = event_json.get('address').split(',')
#     if len(address_arr) == 2:
#         street_address, city = address_arr
#     else:
#         street_address = city = address_arr[0]
#     bar_name = event_json.get('bizname')
#     venue, venue_created = Venue.objects.get_or_create(name=bar_name)
#
#     if venue_created:
#         print('venue created: ' + bar_name + ',city: ' + city)
#
#         venue.city = city
#         gmaps_address = get_gmaps_info(event_json.get('address'))
#         venue.street_address = gmaps_address['formatted_address']
#         venue.longitude, venue.latitude = event_json.get('lng'), event_json.get('lat')
#         venue.phone_number = event_json.get('phone')
#         venue.save()
#
#     # create event
#     defaults = {'venue': venue, 'created_by': easy_scraper_user}
#     event, event_created = Event.objects.get_or_create(title=title, start_time=start_time,
#                                                        defaults=defaults)
#     if event_created:
#         event.categories.add(bars_category)
#         event.image = bars_event_default_image
#         event.save()
#         print('event created: ' + str(event))
#
#     return event, event_created, venue, venue_created
