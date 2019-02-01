import googlemaps

from righthear import settings


def get_gmaps_info(address):
    gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
    geocode_result = gmaps.geocode(address)
    if not geocode_result:
        return None
    formatted_address = geocode_result[0]['formatted_address']
    location = geocode_result[0]['geometry']['location']
    return {'formatted_address': formatted_address, 'lat': location['lat'], 'lng': location['lng']}


def get_event_image(request, event):
    if event.image:
        return request.build_absolute_uri(event.image.url)
    elif event.artist and event.artist.image:
        return request.build_absolute_uri(event.artist.image.url)
    else:
        return None
