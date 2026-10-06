import math
from typing import Tuple, Optional, Dict

# Pre-compiled coordinate reference for NC Research Triangle & regional ZIP codes
NC_ZIP_COORDINATES: Dict[str, Tuple[float, float, str]] = {
    # Wake County (Raleigh, Cary, Apex, Garner, Wake Forest, Morrisville)
    "27601": (35.7721, -78.63861, "Raleigh Downtown, NC"),
    "27603": (35.7369, -78.6475, "South Raleigh, NC"),
    "27604": (35.8105, -78.5833, "East Raleigh, NC"),
    "27605": (35.7891, -78.6575, "Central Raleigh, NC"),
    "27606": (35.7533, -78.7056, "West Raleigh, NC"),
    "27607": (35.8014, -78.6947, "Northwest Raleigh / Blue Ridge, NC"),
    "27608": (35.8078, -78.6417, "Five Points Raleigh, NC"),
    "27609": (35.8453, -78.6253, "North Raleigh, NC"),
    "27610": (35.7678, -78.5683, "Southeast Raleigh, NC"),
    "27611": (35.7796, -78.6382, "Raleigh, NC"),
    "27612": (35.8492, -78.7003, "Crabtree Raleigh, NC"),
    "27613": (35.8892, -78.7183, "Leesville Raleigh, NC"),
    "27614": (35.9186, -78.5997, "North Raleigh / Wakefield, NC"),
    "27615": (35.8753, -78.6253, "North Raleigh / Six Forks, NC"),
    "27616": (35.8833, -78.5417, "Northeast Raleigh, NC"),
    "27617": (35.9083, -78.7667, "Brier Creek Raleigh, NC"),
    "27511": (35.7611, -78.7811, "Cary, NC"),
    "27513": (35.8011, -78.7983, "North Cary, NC"),
    "27518": (35.7231, -78.8028, "South Cary, NC"),
    "27519": (35.8183, -78.8833, "West Cary, NC"),
    "27502": (35.7322, -78.8503, "Apex, NC"),
    "27529": (35.7114, -78.6142, "Garner, NC"),
    "27539": (35.6547, -78.7456, "Apex / Holly Springs, NC"),
    "27540": (35.6514, -78.8336, "Holly Springs, NC"),
    "27545": (35.7761, -78.4892, "Knightdale, NC"),
    "27560": (35.8419, -78.8286, "Morrisville, NC"),
    "27587": (35.9797, -78.5097, "Wake Forest, NC"),
    "27591": (35.8236, -78.3639, "Wendell, NC"),
    "27592": (35.5892, -78.6256, "Willow Spring, NC"),
    "27597": (35.8458, -78.2917, "Zebulon, NC"),

    # Durham County (Durham, RTP)
    "27701": (35.9967, -78.8986, "Downtown Durham, NC"),
    "27702": (35.9940, -78.8986, "Durham Central, NC"),
    "27703": (35.9556, -78.8167, "East Durham, NC"),
    "27704": (36.0389, -78.8833, "North Durham, NC"),
    "27705": (36.0167, -78.9667, "West Durham / Duke, NC"),
    "27707": (35.9667, -78.9333, "Southwest Durham, NC"),
    "27709": (35.9167, -78.8667, "Research Triangle Park (RTP), NC"),
    "27712": (36.1167, -78.9167, "North Durham / Bahama, NC"),
    "27713": (35.9000, -78.9333, "South Durham / Southpoint, NC"),

    # Orange County (Chapel Hill, Carrboro, Hillsborough)
    "27514": (35.9333, -79.0333, "Chapel Hill / East, NC"),
    "27515": (35.9132, -79.0558, "UNC Campus Chapel Hill, NC"),
    "27516": (35.9000, -79.1167, "Chapel Hill / Carrboro, NC"),
    "27517": (35.8667, -79.0333, "South Chapel Hill, NC"),
    "27278": (36.0750, -79.1000, "Hillsborough, NC"),

    # Alamance & Chatham & Johnston (Burlington, Pittsboro, Siler City, Smithfield, Clayton)
    "27215": (36.0833, -79.4333, "Burlington, NC"),
    "27217": (36.1167, -79.4000, "East Burlington, NC"),
    "27312": (35.7167, -79.1833, "Pittsboro, NC"),
    "27344": (35.7250, -79.4611, "Siler City, NC"),
    "27520": (35.6500, -78.4500, "Clayton, NC"),
    "27577": (35.5167, -78.3333, "Smithfield, NC"),

    # Piedmont & State anchors (Greensboro, Winston-Salem, Charlotte, Fayetteville, Wilmington)
    "27401": (36.0726, -79.7920, "Greensboro Downtown, NC"),
    "27101": (36.0999, -80.2442, "Winston-Salem Downtown, NC"),
    "28202": (35.2271, -80.8431, "Charlotte Center City, NC"),
    "28301": (35.0527, -78.8784, "Fayetteville, NC"),
    "28401": (34.2257, -77.9447, "Wilmington, NC"),
}

# Default anchor: Research Triangle centroid
DEFAULT_LAT = 35.8800
DEFAULT_LON = -78.8500


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth in miles.
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 999.0

    R = 3958.8  # Earth radius in miles

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return round(distance, 1)


def geocode_location(location_query: str) -> Tuple[float, float, str]:
    """
    Resolves a location string (e.g. '27514', 'Raleigh', 'Durham') to (lat, lon, label).
    """
    cleaned = location_query.strip().upper()

    # Direct 5-digit ZIP match
    if cleaned in NC_ZIP_COORDINATES:
        lat, lon, label = NC_ZIP_COORDINATES[cleaned]
        return lat, lon, label

    # Fuzzy name match in our database
    for zip_code, (lat, lon, label) in NC_ZIP_COORDINATES.items():
        if cleaned in label.upper():
            return lat, lon, label

    # City defaults
    if "RALEIGH" in cleaned:
        return NC_ZIP_COORDINATES["27601"]
    elif "DURHAM" in cleaned:
        return NC_ZIP_COORDINATES["27701"]
    elif "CHAPEL HILL" in cleaned:
        return NC_ZIP_COORDINATES["27514"]
    elif "CARY" in cleaned:
        return NC_ZIP_COORDINATES["27511"]
    elif "CHARLOTTE" in cleaned:
        return NC_ZIP_COORDINATES["28202"]
    elif "GREENSBORO" in cleaned:
        return NC_ZIP_COORDINATES["27401"]

    # If numeric 5-digit ZIP not in local cache, fallback to Research Triangle center with label
    if cleaned.isdigit() and len(cleaned) == 5:
        return DEFAULT_LAT, DEFAULT_LON, f"ZIP {cleaned} (NC Regional Area)"

    return DEFAULT_LAT, DEFAULT_LON, "Research Triangle, NC"


def get_directions_url(address: str, destination_lat: Optional[float] = None, destination_lon: Optional[float] = None) -> str:
    """Generates Google Maps / OpenStreetMap directions link."""
    clean_addr = address.replace(" ", "+")
    if destination_lat and destination_lon:
        return f"https://www.google.com/maps/dir/?api=1&destination={destination_lat},{destination_lon}"
    return f"https://www.google.com/maps/search/?api=1&query={clean_addr}"
