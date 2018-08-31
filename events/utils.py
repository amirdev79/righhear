import googlemaps

from righthear import settings


def get_address_geocode(address):
    gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
    geocode_result = gmaps.geocode(address)
    location = geocode_result[0]['geometry']['location']
    return location['lat'], location['lng']
