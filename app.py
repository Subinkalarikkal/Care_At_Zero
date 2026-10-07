import streamlit as st
import os
import sys

# Ensure project root is strictly first in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if not sys.path or sys.path[0] != PROJECT_ROOT:
    if PROJECT_ROOT in sys.path:
        sys.path.remove(PROJECT_ROOT)
    sys.path.insert(0, PROJECT_ROOT)

from database.db import get_all_events, init_db, DB_PATH
from data.seed_data import seed_database
from utils.styles import inject_custom_css, render_header, LOGO_PATH
from utils.geo import (
    NC_ZIP_COORDINATES, get_user_current_zip, detect_user_location,
    set_simulated_location, US_SIMULATION_PRESETS, geocode_location, haversine_distance
)


# Set page configuration
st.set_page_config(
    page_title="CareAtZero | Free care. No insurance. Know where to go.",
    page_icon=LOGO_PATH,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize database if needed
if not os.path.exists(DB_PATH):
    seed_database()

# Inject styling
inject_custom_css()

# Render unified top header (CareAtZero banner -> Nav -> Emergency banner)
render_header("home")


# Main Quick Service Launcher & Search Bar
st.markdown("### 🎯 What type of care do you need?")

care_options = [
    "🩺 Medical Care",
    "🦷 Dental Care",
    "👁️ Vision Care",
    "🧠 Behavioral Health"
]
care_mapping = {
    "🩺 Medical Care": "Medical",
    "🦷 Dental Care": "Dental",
    "👁️ Vision Care": "Vision",
    "🧠 Behavioral Health": "Behavioral Health"
}

selected_care_choice = st.selectbox(
    "Select care service needed",
    care_options,
    index=0,
    label_visibility="collapsed",
    key="home_care_type_select"
)

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)


# Quick Location Search Box
user_detected_zip = get_user_current_zip()
saved_loc = st.session_state.get("search_loc")
if not saved_loc or (saved_loc == "27514" and user_detected_zip != "27514"):
    default_loc = user_detected_zip
    st.session_state["search_loc"] = user_detected_zip
else:
    default_loc = saved_loc

loc_info = detect_user_location()
city_label = loc_info.get("city")
location_desc = f"{city_label} ({user_detected_zip})" if city_label else user_detected_zip

with st.form(key="home_quick_search_form", clear_on_submit=False, border=False):
    search_col1, search_col2, search_col3 = st.columns([2, 1, 1])
    with search_col1:
        quick_loc = st.text_input(
            f"📍 **Enter your ZIP Code or City** *(Current Location: {location_desc})*",
            value=default_loc,
            placeholder=f"e.g., {user_detected_zip}, Raleigh, Durham",
            help=f"Press Enter or click Find Free Care to search ({location_desc})",
            key="home_search_loc_input"
        )
    with search_col2:
        quick_timing = st.selectbox("⏱️ **When do you need care?**", ["This Week", "Today", "Flexible (Upcoming)"], index=0)
    with search_col3:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        search_submitted = st.form_submit_button("🔍 Find Free Care Now", type="primary", use_container_width=True)

if search_submitted:
    st.session_state["selected_service"] = care_mapping[selected_care_choice]
    st.session_state["search_loc"] = quick_loc
    st.session_state["search_timing"] = quick_timing
    st.switch_page("pages/1_🔍_Find_Free_Care.py")

if st.query_params.get("test_geo") == "true":
    with st.expander("📍 **Simulate / Test USA Geolocation (Auto-detect Testing)**", expanded=True):
        st.caption("Change simulated US location to test automatic ZIP code detection across different regions.")
        sim_col1, sim_col2 = st.columns([3, 1])
        with sim_col1:
            sim_options = ["Auto-Detect (Current IP)"] + list(US_SIMULATION_PRESETS.keys())
            current_active = "Auto-Detect (Current IP)"
            if "simulated_ip" in st.session_state:
                for k, v in US_SIMULATION_PRESETS.items():
                    if v == st.session_state["simulated_ip"]:
                        current_active = k
                        break
            chosen_sim = st.selectbox(
                "Select USA location to simulate:",
                sim_options,
                index=sim_options.index(current_active) if current_active in sim_options else 0,
                key="sim_loc_dropdown"
            )
        with sim_col2:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Apply Location", key="btn_apply_sim", use_container_width=True):
                if chosen_sim == "Auto-Detect (Current IP)":
                    set_simulated_location(None)
                else:
                    set_simulated_location(chosen_sim)
                st.rerun()

st.markdown("---")

events = get_all_events(include_expired=False, current_date_str="2026-09-16")

# Highlight: Upcoming Mobile Care & RAM Free Clinics
st.subheader("🚐 Upcoming Mobile & Pop-Up Free Care Clinics")
st.markdown("Pop-up clinics provide **100% free episodic care** without insurance, ID, or income documentation. *Arrive early for tickets.*")

# Filter events: ONLY show clinics available directly in that zip code
clean_loc = str(quick_loc).strip()
matching_events = []
for evt in events:
    evt_zip = str(evt.get("zip_code", "")).strip()
    evt_city = str(evt.get("city", "")).strip().lower()
    
    # Exact match on ZIP code
    if clean_loc and clean_loc == evt_zip:
        matching_events.append(evt)
    # Or match if user typed city name (e.g. "Raleigh", "Durham", "Chapel Hill")
    elif clean_loc and not clean_loc.isdigit() and clean_loc.lower() in evt_city:
        matching_events.append(evt)

if matching_events:
    st.markdown(f"**Clinics available in ZIP {clean_loc} ({len(matching_events)} found):**")
    ev_cols = st.columns(min(len(matching_events), 3))
    for idx, evt in enumerate(matching_events[:3]):
        with ev_cols[idx]:
            evt_zip = evt.get('zip_code', '')
            badge_html = f"<span class='badge-event'>📅 {evt.get('date_start')}</span> <span class='badge-free'>FREE</span>"
            st.markdown(f"""
            <div class="care-card" style="height: 100%;">
                <div style="margin-bottom: 8px;">{badge_html}</div>
                <h4 style="margin: 4px 0; color: #1E293B;">{evt.get('title')}</h4>
                <div class="card-meta">📍 {evt.get('location_name')} ({evt.get('city')}, NC {evt_zip})</div>
                <div class="card-meta">🩺 <strong>Services:</strong> {', '.join(evt.get('services', []))}</div>
                <div class="card-meta">⏰ {evt.get('time_details')}</div>
                <div class="source-meta">Verified via {evt.get('organizer_name')} • Source checked Sep 2026</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"View Event Details", key=f"btn_evt_home_{evt.get('id')}", use_container_width=True):
                st.session_state["selected_care_id"] = evt.get("id")
                st.session_state["selected_care_type"] = "event"
                st.switch_page("pages/2_📋_Care_Details.py")
else:
    st.info(f"ℹ️ **No upcoming mobile clinics currently scheduled directly in ZIP {clean_loc}.**")
    st.caption("Use the search bar above or click **🔍 Find Free Care Now** to explore all year-round safety net clinics and free care options.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; font-size: 0.85rem; color: #64748B; padding: 10px 0;'><span style='color: #032C5C; font-weight: 700;'>CareAt</span><span style='color: #01848D; font-weight: 700;'>Zero</span> • Free care. No insurance. Know where to go. • Research Triangle Pilot & National Safety Net Navigator • Version 1.0</div>", unsafe_allow_html=True)



