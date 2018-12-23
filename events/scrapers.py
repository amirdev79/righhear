import datetime
import json
import re

import requests
from django.core.files.images import ImageFile

from events.models import Venue, Event, EventCategory
from events.utils import get_gmaps_info
from righthear import settings
from users.models import UserProfile

EASY_CATEGORIES = {'music': 5818, 'bars': 424, 'theater': 12877, 'standup': 12879}
now = datetime.datetime.now()
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
easy_scraper_user = UserProfile.objects.get(user__username=settings.EASY_CO_IL_USERNAME)
music_category = EventCategory.objects.get(id=1)
music_event_default_image = ImageFile(open("static/images/events/categories_defauls/music_default.jpg", "rb"))


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


def scrape_easy(category):
    events_list = get_events(category)

    if category == 'music':
        events = [_parse_music_event(event) for event in events_list]
    elif category == 'bars':
        events = [_parse_bars_event(event) for event in events_list]
    elif category == 'theater':
        events = [_parse_theater_event(event) for event in events_list]
    elif category == 'standup':
        events = [_parse_standup_event(event) for event in events_list]
    else:
        events = []

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


def _parse_music_event(event_json):
    # get title
    title = event_json['bizname']

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

        start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y|%H:%M')
    else:
        start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y')

    # get venue
    venue_name, city = event_json.get('address').split(',')
    venue, venue_created = Venue.objects.get_or_create(name=venue_name)

    if venue_created:
        print('venue created: ' + venue_name + ',city: ' + city)

        venue.city = city
        gmaps_address = get_gmaps_info(venue_name)
        venue.street_address = gmaps_address['formatted_address']
        venue.longitude, venue.latitude = event_json.get('lng'), event_json.get('lat')
        venue.phone_number = event_json.get('phone')
        venue.save()

    # get price
    price = None
    prop = event_json.get('prop')
    if prop and 'title' in prop[0] and '₪' in prop[0]['title']:
        price = int(re.sub('[^0-9]', '', prop[0]['title']))

    # create event
    defaults = {'venue': venue, 'price': price, 'created_by': easy_scraper_user}
    event, event_created = Event.objects.get_or_create(title=title, start_time=start_time, category= music_category, defaults=defaults)
    if event_created:
        event.image = music_event_default_image
        event.save()
        print ('event created: ' + str(event))

    return event


def _parse_bars_event(event_json):
    title = event_json['bizname'][::-1]
    _date, _time = None, None
    if not 'openhours' in event_json:
        start_time = None
    else:
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
        elif _datetime in ['סגור', 'פתוח']:
            start_time = None
        else:
            start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y')

    return {'title': title, 'start_time': start_time}
