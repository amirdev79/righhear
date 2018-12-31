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
