import csv
import datetime
import json
import re
import tempfile
from itertools import cycle

import requests
from django.contrib.gis.geos import Point
from django.core.files.images import ImageFile
from django.core.mail import EmailMessage
from django.db.models import DateTimeField, CharField, Q
from django.db.models.functions import Cast, TruncSecond

from events.models import Event, Venue, Artist
from events.scrapers.common import wait, get_proxies
from events.utils import get_gmaps_info
from righthear import settings
from users.models import UserProfile

SCRAPER_CATEGORIES = {
    'music': {'easy_id': 5818, 'admin_id': 0, 'sub_category_admin_id': [0],
              'default_image': ImageFile(open("static/images/events/categories_defauls/music_default.jpg", "rb"))},
    'bars': {'easy_id': 424, 'admin_id': 4, 'sub_category_admin_id': [14],
             'default_image': ImageFile(open("static/images/events/categories_defauls/bars_default.jpeg", "rb"))},
    'theater': {'easy_id': 12877, 'admin_id': 5, 'sub_category_admin_id': [8], 'default_image': None},
    'standup': {'easy_id': 12879, 'admin_id': 6, 'sub_category_admin_id': [15], 'default_image': None},
    'movies': {'easy_id': 12953, 'admin_id': 5, 'sub_category_admin_id': [4], 'default_image': None},
    'clubs': {'easy_id': 14527, 'admin_id': 7, 'sub_category_admin_id': [16], 'default_image': None},
    'sports_events': {'easy_id': 15184, 'admin_id': 1, 'sub_category_admin_id': [17], 'default_image': None},
    'sports_activities': {'easy_id': 4917, 'admin_id': 1, 'sub_category_admin_id': [18], 'default_image': None},
    'cafes': {'easy_id': 425, 'admin_id': 2, 'sub_category_admin_id': [19], 'default_image': None},
    'restaurants': {'easy_id': 20015, 'admin_id': 2, 'sub_category_admin_id': [20], 'default_image': None},
    'family': {'easy_id': 21923, 'admin_id': 3, 'sub_category_admin_id': [21, 22], 'default_image': None},
    'spa': {'easy_id': 1585, 'admin_id': 1, 'sub_category_admin_id': [23], 'default_image': None},
    'workshops': {'easy_id': 4920, 'admin_id': 5, 'sub_category_admin_id': [24], 'default_image': None},
}

now = datetime.datetime.now()
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
easy_scraper_user = UserProfile.objects.get(user__username=settings.EASY_CO_IL_USERNAME)

DEFAULTS_FOR_SCRAPER = {'title': '',
                        'description': '',
                        'scraper_username': settings.EASY_CO_IL_USERNAME,
                        'sub_categories': '',
                        'short_description': '',
                        'short_description_heb': '',
                        'description': '',
                        'description_heb': '',
                        'image_url': '',
                        'venue_name': '',
                        'venue_street_address_heb': '',
                        'venue_city': '',
                        'venue_link': '',
                        'end_time': '',
                        'audiences': '',
                        }

CSV_EVENTS_FIELDS = [
    'scraper_username (do not touch)', 'title', 'title_heb', 'start_time', 'end_time', 'artist_id', 'category_id',
    'sub_categories_ids', 'audiences_ids', 'short_description', 'short_description_heb', 'description',
    'description_heb', 'price', 'image_url (do not touch)', 'media_ids', 'venue_id', 'venue_name (do not touch)',
    'venue_name_heb (do not touch)', 'venue_street_address (do not touch)',
    'venue_street_address_heb (do not touch)', 'venue_city (do not touch)', 'venue_city_heb (do not touch)',
    'venue_phone_number (do not touch)', 'venue_longitude (do not touch)',
    'venue_latitude (do not touch)', 'venue_link (do not touch)', 'tickets']

CSV_VENUES_FIELDS = [
    'name', 'name_heb', 'street_address', 'street_address_heb', 'city', 'city_heb', 'phone_number', 'longitude',
    'latitude', 'link'
]


def _to_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%d.%m.%y, %H:%M').astimezone()


def _get_event_page_info(url, proxy):
    info = {}
    page_id = url[url.rindex('/') + 1:]
    url = 'https://easy.co.il/json/bizpage.json?p=' + page_id
    response = requests.get(url, proxies={"http": proxy, "https": proxy})
    event_json = response.json()['bizpage']
    info['text'] = event_json['description']['text']
    info['tickets_link'] = event_json['description']['link']['link']
    return info


def _is_event_exists(event_json, existing_events_cmp_fields):
    parsed_start_time = _get_start_time(event_json)
    if parsed_start_time:
        event_start_datetime = _to_datetime(parsed_start_time)
        db_format_datetime = event_start_datetime.strftime('%Y-%m-%d %H:%M:%S')
    else:
        event_start_datetime = db_format_datetime = None

    event_cmp_fields = event_json['bizname'].strip()[:50], db_format_datetime
    return event_cmp_fields in existing_events_cmp_fields


def _events_category_to_csv(category, proxies):
    print('****************** doing category ' + category + ' ***************')
    events = get_events(category)
    cat_metadata = SCRAPER_CATEGORIES.get(category)

    existing_events_cmp_fields = Event.objects.filter(
        Q(start_time__isnull=True) | Q(start_time__gte=datetime.datetime.now())).annotate(
        start_time_str=Cast(TruncSecond('start_time', DateTimeField()), CharField())).values_list('title_heb',
                                                                                                  'start_time_str')
    new_events = []
    new_venues = []
    existing_venues = Venue.objects.values_list('id', 'name_heb', 'city_heb')
    existing_venues_comparator = [(v[1], v[2]) for v in existing_venues]
    proxy = next(proxies)
    for i, event_json in enumerate(events):
        try:
            print('doing event' + str(i))
            if _is_event_exists(event_json, existing_events_cmp_fields):
                print('event %s is already in DB. excluding from csv...' % event_json['bizname'])
                continue

            # disguise scraping activity
            wait()
            if i % 10 == 0:
                proxy = next(proxies)
                print ('changing proxy to ' + str(proxy))

            parsed = {}
            parsed.update(DEFAULTS_FOR_SCRAPER)
            parsed.update(_parse_event(event_json, category, proxy))
            parsed['category_id'] = str(cat_metadata.get('admin_id'))
            parsed['sub_categories_ids'] = str(cat_metadata.get('sub_category_admin_id')).replace('[', '').replace(']',
                                                                                                                   '')
            parsed_start_time = parsed.get('start_time')
            if parsed_start_time:
                event_start_datetime = _to_datetime(parsed.get('start_time'))
                db_format_datetime = event_start_datetime.strftime('%Y-%m-%d %H:%M:%S')
            else:
                event_start_datetime = db_format_datetime = None

            event_cmp_fields = parsed.get('title_heb').strip()[:50], db_format_datetime
            if event_cmp_fields in existing_events_cmp_fields:
                print('event %s - %s is already in DB. excluding from csv...' % (
                    event_cmp_fields[0], event_cmp_fields[1]))
            elif event_start_datetime and event_start_datetime < datetime.datetime.now().astimezone():
                print('event %s - %s-%s time has passed. excluding from csv...' % (
                    event_cmp_fields[0], parsed.get('start_time'), parsed.get('end_time')))
            else:
                print('new event: ' + str(parsed) + ', cmp_fields: ' + str(event_cmp_fields))

                venue_comparator = (parsed['venue_name_heb'].strip(), parsed['venue_city_heb'].strip())
                try:
                    venue_index = existing_venues_comparator.index(venue_comparator)
                    venue_id = str(existing_venues[venue_index][0])
                    parsed['venue_id'] = venue_id
                    print('venue exists ' + venue_id)
                except ValueError as e:
                    parsed['venue_id'] = ''
                    new_venues.append(
                        ','.join(['"' + parsed.get('venue_' + field, '').replace('"', '""').strip() + '"' for field in
                                  CSV_VENUES_FIELDS]))

                # if venue_index != -1:  # venue exists
                #     venue_id = str(existing_venues[venue_index][0])
                #     parsed['venue_id'] = venue_id
                #     print ('venue exists ' + venue_id)
                # else:
                #     parsed['venue_id'] = ''
                #     new_venues.append(
                #         ','.join(['"' + parsed.get('venue_' + field, '').replace('"', '""').strip() + '"' for field in
                #                   CSV_VENUES_FIELDS]))

                new_events.append(
                    ','.join(['"' + (parsed.get(field, '') or '').replace('"', '""').strip() + '"' for field in
                              CSV_EVENTS_FIELDS]))
        except Exception as e:
            print('*******************could not do event ' + str(event_json) + ': ' + str(e) + ' ******************')

    return new_events, set(new_venues)


def events_to_csv(categories=None):
    new_events = [','.join(CSV_EVENTS_FIELDS)]
    new_venues = [','.join(CSV_VENUES_FIELDS)]
    proxies = cycle(get_proxies())
    for category in categories or SCRAPER_CATEGORIES.keys():
        print('Doing category: ' + category)
        new_events_for_cateogry, new_venues_for_cateogry = _events_category_to_csv(category, proxies)
        new_events += new_events_for_cateogry
        new_venues += new_venues_for_cateogry

    email = EmailMessage(
        'Easy.co.il Events scraper. categories: ' + str(categories),
        'See attached CSV. please update the fields: title, description, short description (non hebrew ones)\nDo not touch the venue fields!',
        settings.DEFAULT_EMAIL,
        [settings.DEFAULT_EMAIL],
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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

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
    _datetime = event_json.get('openhours', 'סגור').replace(' ב-', '|')
    _datetime_arr = _datetime.split('|')
    if len(_datetime_arr) == 2:
        if _datetime_arr[0] == 'היום':
            _datetime = '%s/%s/%s' % (now.day, now.month, now.year) + '|' + _datetime_arr[1]
        elif _datetime_arr[0] == 'מחר':
            _datetime = '%s/%s/%s' % (tomorrow.day, tomorrow.month, tomorrow.year) + '|' + _datetime_arr[1]
        elif _datetime_arr[0].count('/') == 1:
            _datetime = _datetime_arr[0] + '/' + str(now.year) + '|' + _datetime_arr[1]

        start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y|%H:%M').astimezone()
    elif _datetime == 'מחר':
        _datetime = '%s/%s/%s' % (tomorrow.day, tomorrow.month, tomorrow.year)
        start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y').astimezone()
    elif _datetime.count('/') == 1:
        start_time = datetime.datetime.strptime(_datetime + '/' + str(now.year), '%d/%m/%Y').astimezone()
    elif _datetime in ['סגור', 'פתוח']:
        start_time = None
    else:
        start_time = datetime.datetime.strptime(_datetime, '%d/%m/%Y').astimezone()

    return start_time.strftime('%d.%m.%y, %H:%M') if start_time else None


def _get_price(event_json):
    prop = event_json.get('prop')
    if prop and 'title' in prop[0] and '₪' in prop[0]['title']:
        return re.sub('[^0-9]', '', prop[0]['title'])
    else:
        return ''


def _parse_event(event_json, category, proxy):
    event = {'title_heb': event_json['bizname'], 'start_time': _get_start_time(event_json),
             'venue_longitude': event_json['lng'], 'venue_latitude': event_json['lat'],
             'venue_phone_number': event_json.get('phone', '')}

    address = event_json.get('address').split(',')
    if category in ['clubs', 'bars', 'sports_events', 'sports_activities', 'cafes', 'restaurants', 'family', 'spa',
                    'workshops']:
        event['venue_name_heb'] = event_json['bizname']
        if len(address) == 2:
            event['venue_street_address_heb'] = address[0]
            event['venue_city_heb'] = address[1]
        else:
            event['venue_street_address_heb'] = event['venue_city_heb'] = address[0]
    else:
        if len(address) == 2:
            venue_name, city = address
        else:
            venue_name = city = address[0]
        event['venue_name_heb'] = venue_name
        event['venue_city_heb'] = city
        gmaps_address = get_gmaps_info(venue_name)
        if gmaps_address:
            # print (str(gmaps_address))
            address_arr = gmaps_address['formatted_address'].split(',')
            if len(address_arr) == 4:
                event['venue_street_address'] = address_arr[1]
                event['venue_city'] = address_arr[2]
            elif len(address_arr) == 3:
                event['venue_street_address'] = address_arr[0]
                event['venue_city'] = address_arr[1]
            elif len(address_arr) == 2:
                event['venue_street_address'] = address_arr[0]
                event['venue_city'] = address_arr[0]
        else:
            event['venue_street_address'] = event_json['address']

    # gmaps_address = get_gmaps_info(venue_name or city)
    # event['venue_street_address'] = event_json.get('address')
    # event['venue_longitude'] = event_json.get('lng')
    # event['venue_latitude'] = event_json.get('lat')
    # gmaps_address = get_gmaps_info(venue_name or city)
    # event['venue_street_address'] = gmaps_address['formatted_address'] if gmaps_address else event_json['address']
    # event['venue_longitude'] = str(gmaps_address['lng']) if gmaps_address else event_json.get('lng')
    # event['venue_latitude'] = str(gmaps_address['lat']) if gmaps_address else event_json.get('lat')
    event['price'] = _get_price(event_json)
    # print(str(event))

    if category in ['music', 'movies', 'standup', 'theater']:
        additional_info = _get_event_page_info(event_json['url'], proxy)
        event['tickets'] = additional_info['tickets_link']
        event['description_heb'] = additional_info['text']
    return event


def venues_csv_to_db_objects(csv_path):
    # csv_path = '/home/amir/Downloads/tmphkhu5ky7.csv'
    with open(csv_path, 'rt') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for name, name_heb, street_address, street_address_heb, city, city_heb, phone_number, longitude, latitude, link in reader:
            if reader.line_num == 1:
                continue
            ref_location = Point(float(longitude), float(latitude), srid=4326)
            defaults = {'name': name, 'name_heb': name_heb, 'street_address': street_address,
                        'street_address_heb': street_address_heb, 'city': city, 'city_heb': city_heb,
                        'phone_number': phone_number, 'link': link, 'location': ref_location}
            venue, created = Venue.objects.get_or_create(name_heb=name_heb, city_heb=city_heb, defaults=defaults)
            if created:
                print('created venue: ' + name + ', ' + name_heb)
            else:
                print('venue exists: ' + name + ', ' + name_heb)


def events_csv_to_db_objects(csv_path):
    # csv_path = '/home/amir/Downloads/tmpstc4gl24.csv'
    with open(csv_path, 'rt') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for scraper_username, title, title_heb, start_time, end_time, artist_id, category_id, sub_categories, audiences_ids, short_description, short_description_heb, description, description_heb, price, image_url, venue_id, venue_name, venue_name_heb, venue_street_address, venue_street_addresss_heb, venue_city, venue_city_heb, venue_phone_number, venue_longitude, venue_latitude, venue_link, tickets_link in reader:
            print('scraper_username: ' + scraper_username)
            print('title:' + title)
            print('title_heb: ' + title_heb)
            print('start_time: ' + start_time)
            print('end_time: ' + end_time)
            print('artist_id: ' + artist_id)
            print('category_id: ' + category_id)
            print('sub_categories:' + sub_categories)
            print('audiences: ' + audiences_ids)
            print('short_description: ' + short_description)
            print('short_description_heb: ' + short_description_heb)
            print('description: ' + description)
            print('description_heb: ' + description_heb)
            print('price: ' + price)
            print('image_url: ' + image_url)
            print('venue_id: ' + venue_id)
            print('venue_name: ' + venue_name)
            print('venue_name_heb: ' + venue_name_heb)
            print('venue_street_address: ' + venue_street_address)
            print('venue_street_addresss_heb: ' + venue_street_addresss_heb)
            print('venue_city: ' + venue_city)
            print('venue_city_heb: ' + venue_city_heb)
            print('venue_phone_number: ' + venue_phone_number)
            print('venue_longitude: ' + venue_longitude)
            print('venue_latitude: ' + venue_latitude)
            print('venue_link: ' + venue_link)
            print('tickets_link: ' + tickets_link)
            if reader.line_num == 1:
                continue

            start_time = _to_datetime(start_time) if start_time else None
            if len(title_heb) > 50:
                short_description_heb = title_heb
                title_heb = title_heb[:50]
            try:
                venue = Venue.objects.get(id=int(venue_id))
                defaults = {'title': title, 'short_description': short_description,
                            'short_description_heb': short_description_heb, 'description': description,
                            'description_heb': description_heb, 'venue': venue, 'price': price or None,
                            'created_by': easy_scraper_user, 'tickets_link': tickets_link}
                event, created = Event.objects.get_or_create(title_heb=title_heb, start_time=start_time,
                                                             defaults=defaults)
                if created:
                    if artist_id:
                        event.artist = Artist.objects.get(id=int(artist_id))
                    event.categories.add(category_id)
                    if sub_categories:
                        event.sub_categories.add(*sub_categories.split(','))
                    event.image = [cat for cat in SCRAPER_CATEGORIES.values() if cat['admin_id'] == int(category_id)][
                        0].get('default_image')
                    if audiences_ids:
                        event.audiences.add(*audiences_ids.split(','))
                    event.save()
                    print('Event created: ' + str(event))
                else:
                    print('Event already exists: ' + str(event))
            except Exception as e:
                print('skipping event %s - error: %s' % (title_heb, str(e)))

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
