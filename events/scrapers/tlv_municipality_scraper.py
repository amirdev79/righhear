import json
import requests
import datetime
from django.core.files.images import ImageFile
from django.db.models import DateTimeField, CharField
from django.db.models.functions import TruncSecond, Cast

from events.models import EventCategory, Venue, Event, Audience
from events.utils import get_gmaps_info
from righthear import settings
from users.models import UserProfile

CITY = 'תל אביב יפו'
FREE_LABEL = 'לא בתשלום'
TLV_EVENT_DEFAULT_IMAGE = ImageFile(open("static/images/events/categories_defauls/tlv_municipality.png", "rb"))
TLV_SCRAPER_USER = UserProfile.objects.get(user__username=settings.TLV_SCRAPER_USERNAME)
CSV_FIELDS = [
    'scraper_username', 'title', 'title_heb', 'start_time', 'end_time', 'categories', 'sub_categories', 'audiences',
    'short_description', 'short_description_heb', 'description', 'description_heb', 'price', 'image_url', 'venue_name',
    'venue_street_address', 'venue_city', 'venue_phone_number', 'venue_lng', 'venue_lat', 'venue_link']

EVENTS_URL = 'https://www.tel-aviv.gov.il/_vti_bin/TlvSP2013PublicSite/TlvListUtils.svc/getEventsList'
PAYLOAD = {
    "ManagedPropertiesDS": {"Fields": None, "ItemdIds": None, "ListContentTypes": ["סוג תוכן ניהול מאפיינים"],
                            "ListId": "7f58f48c-0d59-434c-b647-5b7a213ba5ab",
                            "SiteId": "24aa409e-01ed-482e-b0ed-1956972addb1",
                            "ViewId": "afb5ff01-6de9-47c4-88aa-b42a45c53795",
                            "WebId": "3af57d92-807c-43c5-8d5f-6fd455eb2776"}, "isDefaultEvents": False,
    "SearchListsCT": "סוג תוכן לאירועים;סוג תוכן אירוע TimeOut", "OrderByField": "TlvStartDate", "CategoryId": 17,
    "AudienceId": 0, "SpecialEventId": 0, "numOfWeeks": 8, "NumOfItems": 200, "listPageSize": 20,
    "pageUrl": "/Pages/MainItemPage.aspx",
    "defaultPicture": "https://www.tel-aviv.gov.il/Lists/designGalleryList/events_default.png", "filtersList": [],
    "filterForMobile": "SpecialEvent",
    "gisUrl": "https://gisn.tel-aviv.gov.il/iview2js/index.aspx?listen=1&hidecontrols=1&zoomslider=1&version=3&btnful=0&btnleg=0&device=desktop&btngeo=1&btnbok=0&btngsv=0&btnclr=0&zoom=1100",
    "eventLinkTitle": "למידע נוסף", "freeEventTitle": "חינם", "displayDates": "True", "displayMap": "False",
    "displayTable": "False", "displayTiles": "True", "defaultDisplay": "Tiles", "isDigitaf": "False",
    "audiencesNotForDisplay": "", "StartDate": None, "EndDate": None}
HEADERS = {'content-type': 'application/json'}

TLV_CATEGORIES_MAP = {
    'outdoors': 17,
    'theater': 19,
    'dance': 21,
    'music': 20,
    'art, exhibitions, conventions': 18,
    'literature & enrichment': 25,
    'entertainment & leisure': 22,
    'moveis': 26,
    'tours': 24,
    'young_kinds': 40,  # digitaf
    'health & sports': 23,
    'kids': 28,
    'community': 27,
}

DEFAULTS_FOR_SCRAPER = {'title': '',
                        'description': '',
                        'scraper_username': settings.TLV_SCRAPER_USERNAME,
                        'sub_categories': '',
                        'short_description': '',
                        'short_description_heb': '',
                        'price': '',
                        'image_url': '',
                        'venue_phone_number': '',
                        'venue_link': '',
                        }


def scrape_tlv(to_csv=True):
    events = get_events()
    if to_csv:
        _events_to_csv(events)
    else:
        _events_to_objects(events)


def _events_to_csv(events):
    existing_events = Event.objects.filter(start_time__gte=datetime.datetime.now()).annotate(
        start_time_str=Cast(TruncSecond('start_time', DateTimeField()), CharField())).values_list('title_heb',
                                                                                            'start_time_str')

    with open('/tmp/events.csv', 'w+') as f:
        lines = [','.join(CSV_FIELDS)]
        for i, event_json in enumerate(events):
            parsed = _parse_event(event_json)
            parsed.update(DEFAULTS_FOR_SCRAPER)
            cmp_fields = tuple(parsed.get('title_heb'), parsed.get('start_time'))
            if _to_datetime(parsed.get('date_time')) >= datetime.datetime.now() and not cmp_fields in existing_events:
                lines.append(','.join(['"' + parsed.get(field, '').replace('"', '""') + '"' for field in CSV_FIELDS]))
            # merge with existing csv file: cat *.csv | sort -u >unique.csv
            print(i)
        f.write('\n'.join(lines))


def _to_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%d.%m.%y, %H:%M').astimezone()


def _events_to_objects(events):
    for event_json in events:
        _add_event_to_db(_parse_event(event_json))


def _add_event_to_db(event_dic):
    _d = lambda field: event_dic.get(field)

    venue, venue_created = Venue.objects.get_or_create(name=_d('venue_name'), city=CITY,
                                                       street_address=_d('venue_street_address'),
                                                       longitude=_d('venue_lng'), latitude=_d('venue_lat'))
    if venue_created:
        print('venue created: %d: %s' % (venue.id, venue.name))

    # create event
    defaults = {'venue': venue, 'price': 0 if _d('is_free') else -1, 'created_by': TLV_SCRAPER_USER,
                'description': _d('description'), 'description_heb': _d('description_heb'),
                'short_description': _d('short_description') or '',
                'short_description_heb': _d('short_description_heb') or '',
                'end_time': _to_datetime(_d('end_time'))}
    print(str(event_dic))
    event, event_created = Event.objects.get_or_create(title_heb=_d('title_heb'),
                                                       start_time=_to_datetime(_d('start_time')),
                                                       defaults=defaults)
    if event_created:
        audiences = Audience.objects.filter(title_heb__in=_d('audiences').split('|'))
        categories = EventCategory.objects.filter(title_heb__in=_d('categories').split('|'))
        event.image = TLV_EVENT_DEFAULT_IMAGE
        event.categories.add(*categories)
        event.audiences.add(*audiences)
        event.save()
        print('event created: ' + str(event))


def _parse_event(event_json):
    parsed_event = {'title_heb': event_json.get('Title'), 'start_time': event_json.get('TlvStartDate'),
                    'venue_name': event_json.get('TlvCityLocation'), 'description_heb': event_json.get('TlvSummary'),
                    'audiences': '|'.join(event_json.get('TlvAudiences').split('\n\n')),
                    'end_time': event_json.get('TlvEndDate'),
                    'categories': '|'.join(event_json.get('TlvItemCategory').split(';')),
                    'is_free': event_json.get('`TlvPaymentRequired') == FREE_LABEL}

    gmaps_address = get_gmaps_info(event_json.get('TlvCityLocation'))
    parsed_event['venue_street_address'] = gmaps_address['formatted_address'] if gmaps_address else 'Unknown'
    parsed_event['venue_lng'] = str(gmaps_address['lng']) if gmaps_address else 'Unknown'
    parsed_event['venue_lat'] = str(gmaps_address['lat']) if gmaps_address else 'Unknown'
    interests = event_json.get('TlvFieldsOfInterests')
    incharge_in_tlv_municipality = event_json.get('TlvInchargeCenter')

    return parsed_event


def scrape_tlv2():
    new_events, new_venues = [], []
    events = get_events()
    for event_json in events:
        event, event_created, venue, venue_created = parse_event(event_json)
        if event_created:
            new_events.append(event.id)
        if venue_created:
            new_venues.append(venue.id)

    print('total events: %d\n\nnew events: %d, ids: %s\n\nnew venues: %d, ids: %s' % (
        len(events), len(new_events), str(new_events), len(new_venues), str(new_venues)))


def get_events():
    json_list = []

    for key in TLV_CATEGORIES_MAP:
        PAYLOAD['CategoryId'] = TLV_CATEGORIES_MAP[key]
        response = requests.post(url=EVENTS_URL, json=PAYLOAD)
        json_list += json.loads(response.content)
    return [{field.get('InternalName'): field.get('Value') for field in e.get('Fields')} for e in json_list]


def parse_event(event_json, to_csv=True):
    # print (str(event_json))

    title = event_json.get('Title')
    start_time = datetime.datetime.strptime(event_json.get('TlvStartDate'), '%d.%m.%y, %H:%M').astimezone()
    venue_name = event_json.get('TlvCityLocation')
    venue_address = event_json.get('TlvAddress1') + ' ' + CITY if event_json.get('TlvAddress1') else event_json.get(
        'Location')
    description = event_json.get('TlvSummary')
    audiences = Audience.objects.filter(title_heb__in=event_json.get('TlvAudiences').split('\n\n'))
    end_time = datetime.datetime.strptime(event_json.get('TlvEndDate'), '%d.%m.%y, %H:%M').astimezone()
    categories = EventCategory.objects.filter(title_heb__in=event_json.get('TlvItemCategory').split(';'))
    interests = event_json.get('TlvFieldsOfInterests')
    incharge_in_tlv_municipality = event_json.get('TlvInchargeCenter')
    is_free = event_json.get('`TlvPaymentRequired') == FREE_LABEL

    gmaps_address = get_gmaps_info(venue_name)
    venue_street_address = gmaps_address['formatted_address'] if gmaps_address else None
    venue_longitude, venue_latitude = gmaps_address['lng'], gmaps_address['lat'] if gmaps_address else None

    if to_csv:
        x = 4
    else:
        venue, venue_created = Venue.objects.get_or_create(name=venue_name)
        if venue_created:
            print('venue created: ' + venue_name + ',city: ' + CITY)

            venue.city = CITY
            if gmaps_address:
                venue.street_address = venue_street_address
                venue.longitude, venue.latitude = venue_longitude, venue_latitude
            else:
                print('could not parse location for venue: ' + str(venue.id) + '- ' + venue.name)
            venue.save()

        # create event
        defaults = {'venue': venue, 'price': 0 if is_free else -1, 'created_by': TLV_SCRAPER_USER,
                    'description': description, 'end_time': end_time}
        event, event_created = Event.objects.get_or_create(title=title, start_time=start_time,
                                                           defaults=defaults)
        if event_created:
            event.image = TLV_EVENT_DEFAULT_IMAGE
            event.categories.add(*categories)
            event.audiences.add(*audiences)
            event.save()
            print('event created: ' + str(event))

        return event, event_created, venue, venue_created

# audiences = set([a for event in events for a in event.get('TlvAudiences').split('\n\n')])
# categories = set([c for e in events for c in e.get('TlvItemCategory').split(';')])
