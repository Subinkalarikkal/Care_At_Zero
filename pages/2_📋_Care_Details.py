import streamlit as st
import os
import sys

# Ensure project root in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db import get_site_by_id, get_event_by_id, is_care_saved, toggle_saved_care
from scoring.care_access_score import calculate_care_access_score
from utils.calendar import generate_ics_calendar
from utils.export import generate_shareable_referral_text
from utils.geo import get_directions_url, geocode_location, haversine_distance, get_user_current_zip
from utils.styles import inject_custom_css, render_header, LOGO_PATH


st.set_page_config(
    page_title="Care Details | CareAtZero",
    page_icon=LOGO_PATH,
    layout="wide"
)

inject_custom_css()
render_header("details")

# Check if a care option is selected in session state
selected_id = st.session_state.get("selected_care_id")
selected_type = st.session_state.get("selected_care_type", "site")

if not selected_id:
    # Default fallback: pick first site or event
    st.info("No specific care option selected. Showing default safety-net option.")
    selected_id = "site_shac_01"
    selected_type = "site"

# Fetch record
if selected_type == "event":
    record = get_event_by_id(selected_id)
else:
    record = get_site_by_id(selected_id)

if not record:
    st.error(f"Care option with ID '{selected_id}' not found.")
    if st.button("⬅️ Return to Search"):
        st.switch_page("pages/1_🔍_Find_Free_Care.py")
    st.stop()

# Basic fields
title = record.get("title") or record.get("name")
cost_class = record.get("cost_class", "Sliding Scale")
is_event = record.get("record_type") == "event"
full_addr = f"{record.get('address')}, {record.get('city')}, {record.get('state')} {record.get('zip_code')}"

# Calculate score breakdown for details
user_loc = st.session_state.get("search_loc") or get_user_current_zip()
u_lat, u_lon, loc_label = geocode_location(user_loc)
dist = haversine_distance(u_lat, u_lon, record.get("latitude"), record.get("longitude"))
score, breakdown, reasons = calculate_care_access_score(
    record=record,
    service_needed="Medical",
    distance_miles=dist,
    reference_date_str="2026-09-16"
)

# Back button & Breadcrumb
col_back, col_dummy = st.columns([1, 4])
with col_back:
    if st.button("⬅️ Back to Results", use_container_width=True):
        st.switch_page("pages/1_🔍_Find_Free_Care.py")

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# Title Header & Badges
cost_badge = "<span class='badge-free'>100% FREE CARE ($0)</span>" if cost_class == "Free" else (
    "<span class='badge-lowcost'>VERY LOW COST ($5-$25)</span>" if cost_class == "Very Low Cost" else "<span class='badge-sliding'>SLIDING SCALE DISCOUNT</span>"
)
type_badge = "<span class='badge-event'>🚐 MOBILE / POP-UP EVENT</span>" if is_event else "<span class='badge-lowcost'>🏥 PERMANENT SAFETY-NET CLINIC</span>"

st.markdown(f"""
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 22px; margin-bottom: 20px;">
    <div style="margin-bottom: 8px;">{cost_badge} {type_badge}</div>
    <h1 style="margin: 4px 0 8px 0; color: #0F172A; font-size: 1.8rem;">{title}</h1>
    <div style="font-size: 0.95rem; color: #475569; margin-bottom: 12px;">
        📍 <strong>{full_addr}</strong> • <span style="color:#2563EB; font-weight:600;">{dist} miles from {user_loc}</span>
    </div>
    <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">
        <span class="score-badge" style="font-size: 0.95rem;">
            ⭐ Care Access Score: <strong>{score}/100</strong>
        </span>
        <span class="trust-pill">
            🛡️ Uninsured Acceptance: {record.get('uninsured_acceptance', 'All Welcome')}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Action Buttons Toolbar
act1, act2, act3 = st.columns(3)

with act1:
    phone_num = record.get("phone", "")
    if phone_num:
        clean_phone = phone_num.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
        st.link_button(f"📞 Call {phone_num}", f"tel:{clean_phone}", type="primary", use_container_width=True)
    else:
        st.button("📞 Phone Not Listed", disabled=True, use_container_width=True)

with act2:
    maps_url = get_directions_url(full_addr, record.get("latitude"), record.get("longitude"))
    st.link_button("🗺️ Get Directions", maps_url, use_container_width=True)

with act3:
    # Add to Calendar (.ics download)
    ics_data = generate_ics_calendar(record)
    file_name = f"careatzero_{record.get('id')}.ics"
    st.download_button(
        label="📅 Add to Calendar (.ics)",
        data=ics_data,
        file_name=file_name,
        mime="text/calendar",
        use_container_width=True
    )

st.markdown("---")

# Two Column Detailed Information
left_col, right_col = st.columns([1.6, 1.4])

with left_col:
    # 1. What to Bring & Readiness Checklist
    st.subheader("📄 What to Bring Checklist")
    st.markdown("*Review and prepare these items before your visit:*")

    docs = record.get("documents_required", [])
    if not docs or "None" in docs[0]:
        st.success("✅ **No ID or income documentation required** for this care event/clinic! (Bring a list of any current prescription medications if taking them).")
    else:
        for doc in docs:
            st.checkbox(f"**{doc}**", key=f"chk_{doc}")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # 2. Timing & Appointment Policy
    st.subheader("⏰ Schedule & Admission Policy")
    if is_event:
        st.markdown(f"""
        - **Event Dates:** {record.get('date_start')} to {record.get('date_end')}
        - **Hours:** {record.get('time_details')}
        - **Intake Rule:** {record.get('appointment_rule')}
        - **Organizer:** {record.get('organizer_name')}
        """)
    else:
        st.markdown(f"""
        - **Operating Hours:** {record.get('hours_summary')}
        - **Appointment Rule:** {record.get('appointment_rule')}
        - **Facility Type:** {record.get('type').upper()}
        """)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # 3. Services Offered
    st.subheader("🩺 Services Offered")
    services = record.get("services", [])
    s_cols = st.columns(min(len(services), 4) or 1)
    for idx, s in enumerate(services):
        with s_cols[idx % len(s_cols)]:
            st.info(f"**{s}**")

    if record.get("notes"):
        st.markdown(f"**Special Notes:** {record.get('notes')}")

with right_col:
    # 4. Care Access Score Breakdown
    st.subheader("🎯 Care Access Score Breakdown")
    st.markdown(f"Care Access Score: **{score}/100** *(Transparent 100-Point Model)*")

    # Score breakdown metric cards
    for signal, pts in breakdown.items():
        st.progress(pts / 35.0 if "35%" in signal else (pts / 25.0 if "25%" in signal else pts / 15.0), text=f"{signal}: **{pts} pts**")

    st.markdown("**Why this matches:**")
    for r in reasons:
        st.markdown(f"- {r}")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # 5. Verified Source & Freshness
    st.subheader("🛡️ Source Provenance & Freshness")
    source_name = record.get("source_name", "Official Directory Feed")
    source_url = record.get("source_url", "https://careatzero.org")
    last_checked = record.get("last_checked", "2026-09-16")
    source_status = record.get("source_status", "active")

    st.markdown(f"""
    - **Primary Source:** [{source_name}]({source_url})
    - **Last Verified Date:** {last_checked}
    - **Feed Status:** <span style="color: {'green' if source_status == 'active' else 'orange'}; font-weight: 600;">{source_status.upper()}</span>
    - **Official Website:** [{record.get('website', source_url)}]({record.get('website', source_url)})
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # 6. Share / Referral Export for Social Workers and Navigators
    st.subheader("📤 Share / Print Referral Summary")
    referral_text = generate_shareable_referral_text(record, score, reasons)
    st.download_button(
        label="📄 Download Referral Summary (.txt)",
        data=referral_text,
        file_name=f"referral_{record.get('id')}.txt",
        mime="text/plain",
        use_container_width=True
    )
    with st.expander("👁️ Preview Shareable Text"):
        st.code(referral_text, language="text")



