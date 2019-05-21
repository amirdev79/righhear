import googlemaps

from righthear import settings
from math import sin, cos, sqrt, atan2, radians


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
        default_image_path = '/static/images/events/categories_defauls/%s_default.jpg' % event.categories.first().icon_name
        return request.build_absolute_uri(default_image_path)


def calculate_distance(from_lng, from_lat, to_lng, to_lat):
    # approximate radius of earth in km
    R = 6373.0

    from_lat = radians(from_lat)
    from_lng = radians(from_lng)
    to_lat = radians(to_lat)
    to_lng = radians(to_lng)

    dlng = to_lng - from_lng
    dlat = to_lat - from_lat

    a = sin(dlat / 2) ** 2 + cos(from_lat) * cos(to_lat) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

