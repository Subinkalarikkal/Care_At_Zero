import streamlit as st
import os
import sys

# Ensure project root in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db import get_all_events, init_db, DB_PATH
from data.seed_data import seed_database
from utils.styles import inject_custom_css, render_header, LOGO_PATH
from utils.geo import NC_ZIP_COORDINATES


# Set page configuration
st.set_page_config(
    page_title="CareAtZero | Free & Low-Cost Healthcare Access",
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
    "🩺 Medical Care (Primary care & exams)",
    "🦷 Dental Care (Extractions & cleanings)",
    "👁️ Vision Care (Free exams & glasses)",
    "🧠 Behavioral Health (Counseling & crisis care)"
]
care_mapping = {
    "🩺 Medical Care (Primary care & exams)": "Medical",
    "🦷 Dental Care (Extractions & cleanings)": "Dental",
    "👁️ Vision Care (Free exams & glasses)": "Vision",
    "🧠 Behavioral Health (Counseling & crisis care)": "Behavioral Health"
}

care_col1, care_col2 = st.columns([3, 1])
with care_col1:
    selected_care_choice = st.selectbox(
        "Select care service needed",
        care_options,
        index=0,
        label_visibility="collapsed",
        key="home_care_type_select"
    )
with care_col2:
    if st.button("Explore Care ➔", key="btn_go_service", use_container_width=True):
        st.session_state["selected_service"] = care_mapping[selected_care_choice]
        st.switch_page("pages/1_🔍_Find_Free_Care.py")

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)


# Quick Location Search Box
search_col1, search_col2, search_col3 = st.columns([2, 1, 1])
with search_col1:
    quick_loc = st.text_input("📍 **Enter your ZIP Code or City** (e.g., 27514, Raleigh, Durham, Cary)", value="27514", placeholder="e.g. 27514")
with search_col2:
    quick_timing = st.selectbox("⏱️ **When do you need care?**", ["This Week", "Today", "Flexible (Upcoming)"], index=0)
with search_col3:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🔍 Find Free Care Now", type="primary", use_container_width=True, key="btn_quick_find_care"):
        st.session_state["selected_service"] = care_mapping[selected_care_choice]
        st.session_state["search_loc"] = quick_loc
        st.session_state["search_timing"] = quick_timing
        st.switch_page("pages/1_🔍_Find_Free_Care.py")

st.markdown("---")

events = get_all_events(include_expired=False, current_date_str="2026-09-16")

# Highlight: Upcoming Mobile Care & RAM Free Clinics
st.subheader("🚐 Upcoming Mobile & Pop-Up Free Care Clinics")
st.markdown("Pop-up clinics provide **100% free episodic care** without insurance, ID, or income documentation. *Arrive early for tickets.*")

ev_cols = st.columns(min(len(events), 3))
for idx, evt in enumerate(events[:3]):
    with ev_cols[idx]:
        badge_html = f"<span class='badge-event'>📅 {evt.get('date_start')}</span> <span class='badge-free'>FREE</span>"
        st.markdown(f"""
        <div class="care-card" style="height: 100%;">
            <div style="margin-bottom: 8px;">{badge_html}</div>
            <h4 style="margin: 4px 0; color: #1E293B;">{evt.get('title')}</h4>
            <div class="card-meta">📍 {evt.get('location_name')} ({evt.get('city')}, NC)</div>
            <div class="card-meta">🩺 <strong>Services:</strong> {', '.join(evt.get('services', []))}</div>
            <div class="card-meta">⏰ {evt.get('time_details')}</div>
            <div class="source-meta">Verified via {evt.get('organizer_name')} • Source checked Sep 2026</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"View Event Details", key=f"btn_evt_home_{evt.get('id')}", use_container_width=True):
            st.session_state["selected_care_id"] = evt.get("id")
            st.session_state["selected_care_type"] = "event"
            st.switch_page("pages/2_📋_Care_Details.py")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; font-size: 0.85rem; color: #64748B; padding: 10px 0;'><span style='color: #032C5C; font-weight: 700;'>CareAt</span><span style='color: #01848D; font-weight: 700;'>Zero</span> • Research Triangle Pilot & National Safety Net Navigator • Version 1.0</div>", unsafe_allow_html=True)



