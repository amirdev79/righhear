import csv
import datetime
import json
import re
import tempfile

import requests
from django.core.files.images import ImageFile
from django.core.mail import EmailMessage
from django.db.models import DateTimeField, CharField
from django.db.models.functions import Cast, TruncSecond

from events.models import Event, EventCategory, Venue
from events.utils import get_gmaps_info
from righthear import settings
from users.models import UserProfile


SCRAPER_CATEGORIES = {
    'music': {'easy_id': 5818, 'admin_id': 0, 'default_image': ImageFile(open("static/images/events/categories_defauls/music_default.jpg", "rb"))},
    'bars': {'easy_id': 424, 'admin_id': 14, 'default_image': ImageFile(open("static/images/events/categories_defauls/bars_default.jpeg", "rb"))},
    'theater': {'easy_id': 12877, 'admin_id': 8, 'default_image':None},
    'standup': {'easy_id': 12879, 'admin_id': 15, 'default_image': None},
}
now = datetime.datetime.now()
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
easy_scraper_user = UserProfile.objects.get(user__username=settings.EASY_CO_IL_USERNAME)

DEFAULTS_FOR_SCRAPER = {'title': '',
                        'description': '' ,
                        'scraper_username': settings.EASY_CO_IL_USERNAME,
                        'sub_categories': '' ,
                        'short_description': '',
                        'short_description_heb': '' ,
                        'description': '',
                        'description_heb': '',
                        'image_url': '',
                        'venue_name': '',
                        'venue_street_address_heb': '',
                        'venue_city': '' ,
                        'venue_link':  '',
                        'end_time':  '',
                        'audiences': '',
                        }

CSV_EVENTS_FIELDS = [
    'scraper_username', 'title', 'title_heb', 'start_time', 'end_time', 'category_id', 'sub_categories', 'audiences',
    'short_description', 'short_description_heb', 'description', 'description_heb', 'price', 'image_url', 'venue_name',
    'venue_name_heb', 'venue_street_address', 'venue_street_addresss_heb', 'venue_city', 'venue_city_heb',
    'venue_phone_number',
    'venue_longitude', 'venue_latitude', 'venue_link']


CSV_VENUES_FIELDS = [
    'name', 'name_heb', 'street_address', 'street_address_heb', 'city', 'city_heb', 'phone_number', 'longitude', 'latitude', 'link'
]


def _to_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%d.%m.%y, %H:%M').astimezone()


def _events_category_to_csv(category):
    events = get_events(category)
    cat_metadata = SCRAPER_CATEGORIES.get(category)

    existing_events_cmp_fields = Event.objects.filter(start_time__gte=datetime.datetime.now()).annotate(
        start_time_str=Cast(TruncSecond('start_time', DateTimeField()), CharField())).values_list('title_heb',
                                                                                                  'start_time_str')
    new_events = []
    new_venues = []
    existing_venues = Venue.objects.values_list('name_heb', flat=True)
    for i, event_json in enumerate(events):
        print('doing event'  + str(i))
        parsed = _parse_event(event_json)
        parsed.update(DEFAULTS_FOR_SCRAPER)
        parsed['category_id'] = str(cat_metadata.get('admin_id'))

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
            new_events.append(
                ','.join(['"' + parsed.get(field, '').replace('"', '""') + '"' for field in CSV_EVENTS_FIELDS]))
            if parsed['venue_name_heb'] not in existing_venues:
                new_venues.append(
                    ','.join(['"' + parsed.get('venue_' + field,'' ).replace('"', '""') + '"' for field in CSV_VENUES_FIELDS]))

    return new_events, set(new_venues)


def events_to_csv():
    new_events = [','.join(CSV_EVENTS_FIELDS)]
    new_venues = [','.join(CSV_VENUES_FIELDS)]
    for category in ['music', 'standup', 'theater']:
        new_events_for_cateogry, new_venues_for_cateogry = _events_category_to_csv(category)
        new_events += new_events_for_cateogry
        new_venues += new_venues_for_cateogry


    email = EmailMessage(
        'Easy.co.il Events scraper',
        'See attached CSV. please update the fields: title, description, short description (non hebrew ones)\nDo not touch the venue fields!',
        'righthearil@gmail.com',
        ['righthearil@gmail.com'],
    )

    events_csv_file = tempfile.NamedTemporaryFile(suffix='.csv')
    with open(events_csv_file.name, 'w+') as f:
        f.write('\n'.join(new_events))

    venues_csv_file = tempfile.NamedTemporaryFile(suffix='.csv')
    with open(venues_csv_file.name, 'w+') as f:
        f.write('\n'.join(new_venues))

    email.attach_file(events_csv_file.name)
    email.attach_file(venues_csv_file.name)
    email.send()


def get_events(category):
    events_list = []
    current_page = 0
    while current_page == 0 or json_list.get('nextpage'):
        url = 'https://easy.co.il/json/list.json?c=' + str(SCRAPER_CATEGORIES.get(category).get('easy_id'))
        if current_page > 0:
            url += '&listpage=' + str(current_page)
        response = requests.get(url)
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

        start_time = datetime.datetime.strptime(_datetime,'%d/%m/%Y|%H:%M').astimezone()
    elif _datetime == 'מחר':
        _datetime = '%s/%s/%s' % (tomorrow.day, tomorrow.month, tomorrow.year)
        start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y').astimezone()
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
    event = {'title_heb': event_json['bizname'], 'start_time': _get_start_time(event_json),
             'venue_longitude': event_json['lng'], 'venue_latitude': event_json['lat'],
             'venue_phone_number': event_json.get('phone', '' )}
    venue_name, city = event_json.get('address').split(',')
    event['venue_name_heb'] = venue_name
    event['venue_city_heb'] = city
    gmaps_address = get_gmaps_info(venue_name)
    event['venue_street_address'] = gmaps_address['formatted_address'] if gmaps_address else event['address']
    event['venue_longitude'] = str(gmaps_address['lng']) if gmaps_address else 0
    event['venue_latitude'] = str(gmaps_address['lat']) if gmaps_address else 0
    event['price'] = _get_price(event_json)
    return event


def venues_csv_to_db_objects(csv_path):
    csv_path = '/home/amir/Downloads/tmphkhu5ky7.csv'
    with open(csv_path, 'rt') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for name, name_heb, street_address, street_address_heb, city, city_heb, phone_number, longitude, latitude, link in reader:
            if reader.line_num == 1:
                continue
            defaults = {'name': name or name_heb, 'street_address': street_address, 'street_address_heb': street_address_heb, 'city': city, 'phone_number': phone_number, 'longitude': longitude, 'latitude': latitude, 'link': link}
            venue, created = Venue.objects.get_or_create(name_heb=name_heb, city_heb=city_heb, defaults=defaults)
            if created:
                print ('created venue: ' + name + ', ' + name_heb)
            else:
                print ('venue exists: ' + name + ', ' + name_heb)


def events_csv_to_db_objects(csv_path):
    csv_path = '/home/amir/Downloads/tmpstc4gl24.csv'
    with open(csv_path, 'rt') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for scraper_username, title, title_heb, start_time, end_time, category_id, sub_categories, audiences, short_description, short_description_heb, description, description_heb, price, image_url, venue_name, venue_name_heb, venue_street_address, venue_street_addresss_heb, venue_city, venue_city_heb, venue_phone_number, venue_longitude, venue_latitude, venue_link in reader:
            # print (scraper_username)
            # print(title)
            # print(title_heb)
            # print(start_time)
            # print(end_time)
            # print(category_id)
            # print(sub_categories)
            # print(audiences)
            # print(short_description)
            # print(short_description_heb)
            # print(description)
            # print(description_heb)
            # print(price)
            # print(image_url)
            # print(venue_name)
            # print(venue_name_heb)
            # print(venue_street_address)
            # print(venue_street_addresss_heb)
            # print(venue_city)
            # print(venue_city_heb)
            # print(venue_phone_number)
            # print(venue_longitude)
            # print(venue_latitude)
            # print(venue_link)
            if reader.line_num == 1:
                continue

            start_time = _to_datetime(start_time)
            try:
                venue = Venue.objects.get(name_heb=venue_name_heb, city_heb = venue_city_heb)
                defaults = {'title': title, 'short_description': short_description, 'short_description_heb': short_description_heb , 'description': description, 'description_heb': description_heb, 'venue': venue, 'price': price or None, 'created_by': easy_scraper_user}
                event, created = Event.objects.get_or_create(title_heb=title_heb, start_time=start_time, defaults=defaults)
                if created:
                    event.categories.add(category_id)
                    if sub_categories:
                        event.sub_categories.add(*sub_categories.split(','))
                    event.image = [cat for cat in SCRAPER_CATEGORIES.values() if cat['admin_id'] == int(category_id)][0].get('default_image')
                    event.save()
            except Exception as e:
                print ('skipping event %s - error: %s' % (title_heb, str(e)))


# def _parse_bars_event(event_json):
#     title = event_json[bizname]
#     _date, _time = None, None
#     if not openhours in event_json:
#         start_time = None
#     else:
#         _datetime = event_json[openhours].replace( ב-, |)
#         _datetime_arr = _datetime.split(|)
#         if len(_datetime_arr) == 2:
#             if _datetime_arr[0] == היום:
#                 _datetime = %s/%s/%s % (now.day, now.month, now.year) + | + _datetime_arr[1]
#             elif _datetime_arr[0] == מחר:
#                 _datetime = %s/%s/%s % (tomorrow.day, tomorrow.month, tomorrow.year) + | + _datetime_arr[1]
#             elif _datetime_arr[0].count(/) == 1:
#                 _datetime = _datetime_arr[0] + / + str(now.year) + | + _datetime_arr[1]
#
#             start_time = datetime.datetime.strptime(_datetime, %d/%m/%Y|%H:%M)
#         elif _datetime in [סגור, פתוח]:
#             start_time = None
#         else:
#             start_time = datetime.datetime.strptime(_datetime, %d/%m/%Y)
#
#     # get venue
#     address_arr = event_json.get(address).split(,)
#     if len(address_arr) == 2:
#         street_address, city = address_arr
#     else:
#         street_address = city = address_arr[0]
#     bar_name = event_json.get(bizname)
#     venue, venue_created = Venue.objects.get_or_create(name=bar_name)
#
#     if venue_created:
#         print(venue created:  + bar_name + ,city:  + city)
#
#         venue.city = city
#         gmaps_address = get_gmaps_info(event_json.get(address))
#         venue.street_address = gmaps_address[formatted_address]
#         venue.longitude, venue.latitude = event_json.get(lng), event_json.get(lat)
#         venue.phone_number = event_json.get(phone)
#         venue.save()
#
#     # create event
#     defaults = {venue: venue, created_by: easy_scraper_user}
#     event, event_created = Event.objects.get_or_create(title=title, start_time=start_time,
#                                                        defaults=defaults)
#     if event_created:
#         event.categories.add(bars_category)
#         event.image = bars_event_default_image
#         event.save()
#         print(event created:  + str(event))
#
#     return event, event_created, venue, venue_created
