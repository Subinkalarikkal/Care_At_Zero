"""
CareAtZero Utilities Package.
"""
from utils.geo import (
    NC_ZIP_COORDINATES,
    get_user_current_zip,
    detect_user_location,
    set_simulated_location,
    US_SIMULATION_PRESETS,
    geocode_location,
    haversine_distance,
    inject_client_geo_detector,
    safe_city_name
)
from utils.styles import inject_custom_css, render_header, LOGO_PATH

