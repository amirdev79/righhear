import json
import requests
import datetime

from django.core.files.images import ImageFile

from events.models import EventCategory, Venue, Event, Audience
from events.utils import get_gmaps_info
from righthear import settings
from users.models import UserProfile

city = 'תל אביב יפו'
free_label = 'לא בתשלום'
tlv_event_default_image = ImageFile(open("static/images/events/categories_defauls/tlv_municipality.png", "rb"))
tlv_scraper_user = UserProfile.objects.get(user__username=settings.TLV_SCRAPER_USERNAME)

events_url = 'https://www.tel-aviv.gov.il/_vti_bin/TlvSP2013PublicSite/TlvListUtils.svc/getEventsList'
outdoors_payload = {
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
headers = {'content-type': 'application/json'}

tlv_categories_map = {
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


def scrape_tlv():
    new_events, new_venues = [], []
    events = get_events()
    for event_json in events:
        event, event_created, venue, venue_created = parse_event(event_json)
        if event_created:
            new_events.append(event.id)
        if venue_created:
            new_venues.append(venue.id)

    print ('total events: %d\n\nnew events: %d, ids: %s\n\nnew venues: %d, ids: %s' % (len(events), len(new_events), str(new_events), len(new_venues), str(new_venues)))


def get_events():
    json_list = []

    for key in tlv_categories_map:
        outdoors_payload['CategoryId'] = tlv_categories_map[key]
        response = requests.post(url=events_url, json=outdoors_payload)
        json_list += json.loads(response.content)
    return [{field.get('InternalName'): field.get('Value') for field in e.get('Fields')} for e in json_list]


def parse_event(event_json):

    print (str(event_json))

    title = event_json.get('Title')
    start_time = datetime.datetime.strptime(event_json.get('TlvStartDate'), '%d.%m.%y, %H:%M')
    venue_name = event_json.get('TlvCityLocation')
    venue_address = event_json.get('TlvAddress1') + ' ' + city if event_json.get('TlvAddress1') else event_json.get(
        'Location')
    description = event_json.get('TlvSummary')
    audiences = Audience.objects.filter(title_heb__in=event_json.get('TlvAudiences').split('\n\n'))
    end_time = datetime.datetime.strptime(event_json.get('TlvEndDate'), '%d.%m.%y, %H:%M')
    categories = EventCategory.objects.filter(title_heb__in=event_json.get('TlvItemCategory').split(';'))
    interests = event_json.get('TlvFieldsOfInterests')
    incharge_in_tlv_municipality = event_json.get('TlvInchargeCenter')
    is_free = event_json.get('`TlvPaymentRequired') == free_label

    venue, venue_created = Venue.objects.get_or_create(name=venue_name)
    if venue_created:
        print('venue created: ' + venue_name + ',city: ' + city)

        venue.city = city
        gmaps_address = get_gmaps_info(venue_name)
        if gmaps_address:
            venue.street_address = gmaps_address['formatted_address']
            venue.longitude, venue.latitude = gmaps_address['lng'], gmaps_address['lat']
        else:
            print ('could not parse location for venue: ' + str(venue.id) + '- ' + venue.name)
        venue.save()

    # create event
    defaults = {'venue': venue, 'price': 0 if is_free else -1, 'created_by': tlv_scraper_user, 'description': description, 'end_time':end_time}
    event, event_created = Event.objects.get_or_create(title=title, start_time=start_time,
                                                       defaults=defaults)
    if event_created:
        event.image = tlv_event_default_image
        event.categories.add(*categories)
        event.audiences.add(*audiences)
        event.save()
        print('event created: ' + str(event))

    return event, event_created, venue, venue_created


# audiences = set([a for event in events for a in event.get('TlvAudiences').split('\n\n')])
# categories = set([c for e in events for c in e.get('TlvItemCategory').split(';')])