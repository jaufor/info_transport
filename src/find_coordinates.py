from geopy.geocoders import Nominatim
from geopy.point import Point

geolocator = Nominatim(user_agent="info_transport")

def get_coordinates(query):
    """
    Get the geographic coordinates of a postal address of Madrid from the Nominatim geocoding service.

    Args:
    Dictionary with keys: street (String) and city (String)

    Side effects:
    Prints retrieved address to confirm that it's the one that is looked for
    
    Returns:
    Tuple: latitude (Float) and longitude (Float) coordinates
    """
    location = geolocator.geocode(query, viewbox=[Point(40.55, -4), Point(40.25, -3.3)], bounded=True)
    print(location.address)
    return (location.latitude, location.longitude)


