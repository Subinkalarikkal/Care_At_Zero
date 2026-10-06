import streamlit as st
import os
import sys

# Ensure project root in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db import get_all_sites, get_all_events, init_db, DB_PATH
from data.seed_data import seed_database
from utils.styles import inject_custom_css, render_header
from utils.geo import NC_ZIP_COORDINATES


# Set page configuration
st.set_page_config(
    page_title="CareAtZero | Free & Low-Cost Healthcare Access",
    page_icon="🩺",
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
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    if st.button("🩺 **Medical Care**\n\n*Primary care & exams*", use_container_width=True):
        st.session_state["selected_service"] = "Medical"
        st.switch_page("pages/1_🔍_Find_Free_Care.py")
with row1_col2:
    if st.button("🦷 **Dental Care**\n\n*Extractions & cleanings*", use_container_width=True):
        st.session_state["selected_service"] = "Dental"
        st.switch_page("pages/1_🔍_Find_Free_Care.py")

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    if st.button("👁️ **Vision Care**\n\n*Free exams & glasses*", use_container_width=True):
        st.session_state["selected_service"] = "Vision"
        st.switch_page("pages/1_🔍_Find_Free_Care.py")
with row2_col2:
    if st.button("🧠 **Behavioral Health**\n\n*Counseling & crisis care*", use_container_width=True):
        st.session_state["selected_service"] = "Behavioral Health"
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
    if st.button("🔍 Find Free Care Now", type="primary", use_container_width=True):
        st.session_state["search_loc"] = quick_loc
        st.session_state["search_timing"] = quick_timing
        st.switch_page("pages/1_🔍_Find_Free_Care.py")

st.markdown("---")

# Impact & Coverage Metrics
sites = get_all_sites()
events = get_all_events(include_expired=False, current_date_str="2026-09-16")
free_sites_count = sum(1 for s in sites if s.get("cost_class") == "Free")
sliding_sites_count = sum(1 for s in sites if s.get("cost_class") == "Sliding Scale")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(sites)}</div>
        <div class="stat-label">Verified Safety Net Clinics</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{free_sites_count}</div>
        <div class="stat-label">100% Free Clinics ($0 Fee)</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(events)}</div>
        <div class="stat-label">Upcoming Mobile / Pop-Up Events</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">100%</div>
        <div class="stat-label">Source Transparent & Free</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

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

st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

# How CareAtZero Works (UX Principles)
st.subheader("💡 Why CareAtZero is Different")
p1, p2, p3 = st.columns(3)

with p1:
    st.markdown("""
    #### 🟢 1. Clear Cost Labels First
    We clearly classify every option:
    - **Free**: $0 patient charge verified.
    - **Very Low Cost**: $5–$25 nominal fee.
    - **Sliding Scale**: Discounts based on income.
    *Never guessing or surprising you with normal pricing.*
    """)

with p2:
    st.markdown("""
    #### 🎯 2. Transparent Care Access Score
    We rank options not just by distance, but by:
    - Cost fit (35%)
    - Upcoming availability / walk-in (25%)
    - Service match (15%)
    - Eligibility & document readiness (10%)
    - Distance & data freshness (15%)
    """)

with p3:
    st.markdown("""
    #### 🔒 3. Zero Cost & Complete Privacy
    - **No login or registration required**
    - **No medical history, SSN, or diagnosis stored**
    - **Zero cost forever** for patients, navigators, and community organizations.
    """)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; font-size: 0.85rem; color: #64748B; padding: 10px 0;'>CareAtZero • Research Triangle Pilot & National Safety Net Navigator • Version 1.0</div>", unsafe_allow_html=True)



