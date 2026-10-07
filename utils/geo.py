import math
import urllib.request
import json
import os
from typing import Tuple, Optional, Dict, Any

_CACHED_USER_LOCATION: Optional[Dict[str, Any]] = None
DEFAULT_FALLBACK_ZIP = "27514"

# Pre-configured US Location simulation IPs
US_SIMULATION_PRESETS: Dict[str, str] = {
    "Raleigh, NC": "152.1.0.1",
    "Chapel Hill, NC": "152.2.0.1",
    "New York, NY": "128.122.1.1",
    "Pasadena / Los Angeles, CA": "131.215.1.1",
    "Mountain View, CA": "66.249.66.1",
    "Pittsburgh, PA": "128.2.0.1",
}


def safe_city_name(city: str) -> str:
    """Sanitizes city names to prevent unicode encoding errors on various platforms."""
    if not city:
        return ""
    import unicodedata
    normalized = unicodedata.normalize('NFKD', str(city))
    cleaned = normalized.encode('ascii', 'ignore').decode('ascii').strip()
    return cleaned or str(city)


def is_valid_public_ip(ip: str) -> bool:
    """Checks whether an IP address is a valid public, routable IP."""
    try:
        import ipaddress
        obj = ipaddress.ip_address(ip.strip())
        return not (obj.is_private or obj.is_loopback or obj.is_reserved or obj.is_link_local or obj.is_multicast)
    except Exception:
        return False


def get_client_ip() -> Optional[str]:
    """
    Extracts the user's real client IP from Streamlit context headers.
    Checks Cloudflare (cf-connecting-ip), X-Real-IP, X-Forwarded-For,
    and Streamlit's context.ip_address.
    """
    try:
        import streamlit as st
        if hasattr(st, "context"):
            headers = getattr(st.context, "headers", None)
            if headers:
                for h in ["cf-connecting-ip", "x-real-ip", "x-forwarded-for"]:
                    val = headers.get(h)
                    if val:
                        parts = [p.strip() for p in val.split(",") if p.strip()]
                        for candidate in parts:
                            if is_valid_public_ip(candidate):
                                return candidate

            st_ip = getattr(st.context, "ip_address", None)
            if st_ip and is_valid_public_ip(st_ip):
                return st_ip.strip()
    except Exception:
        pass
    return None


def is_cloud_environment() -> bool:
    """Detects if running on Streamlit Cloud, container, or cloud host."""
    if os.path.exists("/mount/src"):
        return True
    if os.getenv("STREAMLIT_SHARING_MODE") is not None:
        return True
    if os.getenv("STREAMLIT_SERVER_BASE_URL_PATH") is not None:
        return True
    return False


def is_datacenter_location(loc: Dict[str, Any]) -> bool:
    """Detects if the detected location belongs to a cloud hosting datacenter instead of a real user."""
    city = str(loc.get("city", "")).lower()
    zip_code = str(loc.get("zip", "")).strip()

    # Google Cloud Oregon datacenter (The Dalles, Wasco County, OR 97058)
    if zip_code == "97058" or "the dalles" in city:
        return True
    # AWS / GCP Boardman OR
    if zip_code == "97818" or "boardman" in city:
        return True
    # Ashburn / Sterling VA AWS datacenter clusters
    if zip_code in ("20147", "20166", "20149") and ("ashburn" in city or "sterling" in city):
        return True
    return False


def inject_client_geo_detector():
    """
    Injects a client-side detector that fetches the user's real location directly in their browser
    (phone or desktop), prioritizing HTML5 GPS coordinates, then ipinfo.io, then fallback services.
    """
    try:
        import streamlit as st
        import streamlit.components.v1 as components

        # Skip if already resolved in session_state
        if hasattr(st, "session_state"):
            loc = st.session_state.get("detected_user_location")
            if loc and loc.get("source") in ("client_browser", "simulated_zip", "simulated_ip"):
                return

        if hasattr(st, "query_params"):
            if st.query_params.get("client_zip") or st.query_params.get("geo_checked") or st.query_params.get("simulated_zip"):
                return

        js_detector = """
        <script>
        (function() {
            try {
                var pLoc = window.parent.location;
                var url = new URL(pLoc.href);
                if (url.searchParams.get("client_zip") || url.searchParams.get("geo_checked") || url.searchParams.get("simulated_zip")) {
                    return;
                }

                async function applyGeo(zip, city, lat, lon) {
                    if (zip) url.searchParams.set("client_zip", zip);
                    if (city) url.searchParams.set("client_city", city);
                    if (lat) url.searchParams.set("client_lat", lat);
                    if (lon) url.searchParams.set("client_lon", lon);
                    url.searchParams.set("geo_checked", "1");
                    try {
                        pLoc.replace(url.href);
                    } catch(e) {
                        window.location.replace(url.href);
                    }
                }

                async function detectLocation() {
                    // 1. Try HTML5 Geolocation (GPS hardware on mobile / Wi-Fi positioning on desktop)
                    if (navigator.geolocation) {
                        try {
                            var position = await new Promise(function(resolve, reject) {
                                navigator.geolocation.getCurrentPosition(resolve, reject, {
                                    timeout: 3000,
                                    maximumAge: 120000,
                                    enableHighAccuracy: true
                                });
                            });
                            if (position && position.coords) {
                                var lat = position.coords.latitude;
                                var lon = position.coords.longitude;
                                // Reverse-geocode via Nominatim
                                try {
                                    var nomResp = await fetch("https://nominatim.openstreetmap.org/reverse?format=json&lat=" + lat + "&lon=" + lon, { cache: "no-store" });
                                    if (nomResp.ok) {
                                        var nomData = await nomResp.json();
                                        var addr = nomData.address || {};
                                        var zip = addr.postcode;
                                        var city = addr.city || addr.town || addr.village || addr.suburb || addr.county || "";
                                        if (zip) {
                                            applyGeo(zip, city, lat, lon);
                                            return;
                                        }
                                    }
                                } catch(e) {}
                                // Reverse-geocode via BigDataCloud
                                try {
                                    var bdcResp = await fetch("https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=" + lat + "&longitude=" + lon + "&localityLanguage=en", { cache: "no-store" });
                                    if (bdcResp.ok) {
                                        var bdcData = await bdcResp.json();
                                        var zip = bdcData.postcode;
                                        var city = bdcData.locality || bdcData.city || "";
                                        if (zip) {
                                            applyGeo(zip, city, lat, lon);
                                            return;
                                        }
                                    }
                                } catch(e) {}
                            }
                        } catch(geoErr) {
                            // GPS denied or timed out, fall through to IP detection
                        }
                    }

                    // 2. Primary IP service: ipinfo.io (most accurate for Indian and US networks)
                    try {
                        var rInfo = await fetch("https://ipinfo.io/json", { cache: "no-store" });
                        if (rInfo.ok) {
                            var dInfo = await rInfo.json();
                            if (dInfo && dInfo.postal) {
                                var lat = null, lon = null;
                                if (dInfo.loc) {
                                    var parts = dInfo.loc.split(",");
                                    lat = parts[0]; lon = parts[1];
                                }
                                applyGeo(dInfo.postal, dInfo.city || "", lat, lon);
                                return;
                            }
                        }
                    } catch(e) {}

                    // 3. Secondary IP service: ipapi.co
                    try {
                        var rCo = await fetch("https://ipapi.co/json/", { cache: "no-store" });
                        if (rCo.ok) {
                            var dCo = await rCo.json();
                            if (dCo && dCo.postal) {
                                applyGeo(dCo.postal, dCo.city || "", dCo.latitude, dCo.longitude);
                                return;
                            }
                        }
                    } catch(e) {}

                    // 4. Tertiary IP service: freeipapi
                    try {
                        var rFree = await fetch("https://freeipapi.com/api/json", { cache: "no-store" });
                        if (rFree.ok) {
                            var dFree = await rFree.json();
                            if (dFree && dFree.zipCode) {
                                applyGeo(dFree.zipCode, dFree.cityName || "", dFree.latitude, dFree.longitude);
                                return;
                            }
                        }
                    } catch(e) {}

                    // If all failed, mark geo_checked so it does not loop
                    url.searchParams.set("geo_checked", "1");
                    try { pLoc.replace(url.href); } catch(e) { window.location.replace(url.href); }
                }

                detectLocation();
            } catch(err) {
                console.warn("Client geo skipped:", err);
            }
        })();
        </script>
        """
        components.html(js_detector, height=0, width=0)
    except Exception:
        pass


def set_simulated_location(ip_or_preset: Optional[str] = None, force_zip: Optional[str] = None) -> Dict[str, Any]:
    """
    Overrides the current user location with a simulated US location/IP.
    Clears cache and forces immediate refresh.
    """
    global _CACHED_USER_LOCATION
    _CACHED_USER_LOCATION = None

    sim_ip = US_SIMULATION_PRESETS.get(ip_or_preset, ip_or_preset) if ip_or_preset else None

    try:
        import streamlit as st
        if hasattr(st, "session_state"):
            if sim_ip:
                st.session_state["simulated_ip"] = sim_ip
            else:
                st.session_state.pop("simulated_ip", None)

            if force_zip:
                st.session_state["simulated_zip"] = force_zip
            else:
                st.session_state.pop("simulated_zip", None)

            st.session_state.pop("detected_user_location", None)
            st.session_state.pop("search_loc", None)
    except Exception:
        pass

    return detect_user_location(force_refresh=True, simulated_ip=sim_ip)


def detect_user_location(force_refresh: bool = False, simulated_ip: Optional[str] = None) -> Dict[str, Any]:
    """
    Detects the user's current geographic location and postal/ZIP code via client browser or IP geolocation.
    Supports client browser query params, client IP headers, simulated US IPs,
    and automatic rejection of cloud datacenter locations (e.g. The Dalles, OR 97058).
    Returns a dictionary with 'zip', 'city', 'region', 'country', 'lat', 'lon', 'source'.
    """
    global _CACHED_USER_LOCATION

    # Resolve simulation parameters
    target_ip = simulated_ip or os.getenv("CARE_SIMULATED_IP")
    target_zip = os.getenv("CARE_SIMULATED_ZIP")

    try:
        import streamlit as st
        # 1. First priority: Check if client browser passed its directly detected ZIP code
        if hasattr(st, "query_params") and not target_ip and not target_zip:
            if "client_zip" in st.query_params:
                c_zip = str(st.query_params["client_zip"]).strip()
                c_city = safe_city_name(st.query_params.get("client_city", ""))
                c_lat = None
                c_lon = None
                if "client_lat" in st.query_params and "client_lon" in st.query_params:
                    try:
                        c_lat = float(st.query_params["client_lat"])
                        c_lon = float(st.query_params["client_lon"])
                    except Exception:
                        pass
                client_loc = {
                    "zip": c_zip,
                    "city": c_city or "Current Location",
                    "region": "",
                    "country": "",
                    "lat": c_lat,
                    "lon": c_lon,
                    "source": "client_browser"
                }
                if hasattr(st, "session_state"):
                    st.session_state["detected_user_location"] = client_loc
                _CACHED_USER_LOCATION = client_loc
                # Remove client_zip from query_params to keep the URL clean and avoid overriding user searches
                st.query_params.pop("client_zip", None)
                st.query_params.pop("client_city", None)
                st.query_params.pop("client_lat", None)
                st.query_params.pop("client_lon", None)
                return client_loc

            if "simulated_ip" in st.query_params:
                target_ip = st.query_params["simulated_ip"]
            if "simulated_zip" in st.query_params:
                target_zip = st.query_params["simulated_zip"]

        if hasattr(st, "session_state"):
            if not target_ip and "simulated_ip" in st.session_state:
                target_ip = st.session_state["simulated_ip"]
            if not target_zip and "simulated_zip" in st.session_state:
                target_zip = st.session_state["simulated_zip"]

            # Per-session caching check (isolated per user)
            if not force_refresh and not target_ip and not target_zip:
                sess_loc = st.session_state.get("detected_user_location")
                if sess_loc and sess_loc.get("source") != "fallback" and not is_datacenter_location(sess_loc):
                    return sess_loc
    except Exception:
        pass

    # Outside Streamlit (e.g. pytest): check global cache if valid
    if _CACHED_USER_LOCATION is not None and _CACHED_USER_LOCATION.get("source") != "fallback" and not force_refresh and not target_ip and not target_zip and not is_datacenter_location(_CACHED_USER_LOCATION):
        return _CACHED_USER_LOCATION

    # If target_zip is directly specified
    if target_zip:
        loc = {
            "zip": str(target_zip).strip(),
            "city": "Simulated City",
            "region": "US",
            "country": "United States",
            "lat": 35.7721,
            "lon": -78.6386,
            "source": "simulated_zip"
        }
        _CACHED_USER_LOCATION = loc
        try:
            import streamlit as st
            if hasattr(st, "session_state"):
                st.session_state["detected_user_location"] = loc
        except Exception:
            pass
        return loc

    # If target_ip not explicitly set, extract real client IP from incoming request
    if not target_ip:
        client_ip = get_client_ip()
        if client_ip:
            target_ip = client_ip

    # If we are in a cloud environment and target_ip is STILL None:
    # Do NOT query https://ipinfo.io/json with no IP, because that will resolve
    # the server container IP in The Dalles, Oregon!
    if is_cloud_environment() and not target_ip:
        fallback = {
            "zip": DEFAULT_FALLBACK_ZIP,
            "city": "Chapel Hill",
            "region": "NC",
            "country": "US",
            "lat": 35.9333,
            "lon": -79.0333,
            "source": "fallback"
        }
        return fallback

    # Determine services endpoints
    if target_ip:
        services = [
            (f"https://freeipapi.com/api/json/{target_ip}", "zipCode", "cityName", "regionName", "countryName"),
            (f"https://ipinfo.io/{target_ip}/json", "postal", "city", "region", "country"),
        ]
    else:
        # Local development on developer's machine: query own IP
        services = [
            ("https://ipinfo.io/json", "postal", "city", "region", "country"),
            ("https://freeipapi.com/api/json", "zipCode", "cityName", "regionName", "countryName"),
        ]

    detected = None
    for url, zip_k, city_k, reg_k, cntry_k in services:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "curl/7.88.1 (CareAtZero/1.0)"})
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
                z = data.get(zip_k)
                if z:
                    z_clean = str(z).strip()
                    lat = data.get("latitude")
                    lon = data.get("longitude")
                    if lat is None and "loc" in data:
                        parts = data["loc"].split(",")
                        if len(parts) == 2:
                            lat = float(parts[0])
                            lon = float(parts[1])

                    loc_candidate = {
                        "zip": z_clean,
                        "city": safe_city_name(str(data.get(city_k) or "")),
                        "region": safe_city_name(str(data.get(reg_k) or "")),
                        "country": str(data.get(cntry_k) or "").strip(),
                        "lat": float(lat) if lat is not None else None,
                        "lon": float(lon) if lon is not None else None,
                        "source": url
                    }

                    # Verify candidate is NOT a cloud datacenter
                    if not is_datacenter_location(loc_candidate):
                        detected = loc_candidate
                        break
        except Exception:
            continue

    if detected:
        _CACHED_USER_LOCATION = detected
        try:
            import streamlit as st
            if hasattr(st, "session_state"):
                st.session_state["detected_user_location"] = detected
        except Exception:
            pass
        return detected

    # Return fallback without poisoning cache
    fallback = {
        "zip": DEFAULT_FALLBACK_ZIP,
        "city": "Chapel Hill",
        "region": "NC",
        "country": "US",
        "lat": 35.9333,
        "lon": -79.0333,
        "source": "fallback"
    }
    return fallback


def get_user_current_zip() -> str:
    """
    Returns the user's current detected ZIP/postal code based on their actual location,
    falling back to 27514 if location detection is unavailable.
    """
    loc = detect_user_location()
    return loc.get("zip") or DEFAULT_FALLBACK_ZIP


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
    Dynamically checks the user's detected location if the query matches their ZIP.
    """
    cleaned = location_query.strip().upper()

    # Direct ZIP match in known NC coordinate table
    if cleaned in NC_ZIP_COORDINATES:
        lat, lon, label = NC_ZIP_COORDINATES[cleaned]
        return lat, lon, label

    # Check if query matches user's current detected location
    user_loc = detect_user_location()
    if user_loc and cleaned == str(user_loc.get("zip", "")).upper():
        if user_loc.get("lat") is not None and user_loc.get("lon") is not None:
            city_str = user_loc.get("city") or "Current Location"
            reg_str = user_loc.get("region") or ""
            label = f"{city_str}, {reg_str} ({cleaned})".strip(" ,")
            return user_loc["lat"], user_loc["lon"], label

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

    # Numeric ZIP (5 or 6 digit) not in local cache
    if cleaned.isdigit():
        return DEFAULT_LAT, DEFAULT_LON, f"ZIP {cleaned} (Area)"

    return DEFAULT_LAT, DEFAULT_LON, "Research Triangle, NC"


def get_directions_url(address: str, destination_lat: Optional[float] = None, destination_lon: Optional[float] = None) -> str:
    """Generates Google Maps / OpenStreetMap directions link."""
    clean_addr = address.replace(" ", "+")
    if destination_lat and destination_lon:
        return f"https://www.google.com/maps/dir/?api=1&destination={destination_lat},{destination_lon}"
    return f"https://www.google.com/maps/search/?api=1&query={clean_addr}"
