import streamlit as st
import os
import sys
import folium
from streamlit_folium import st_folium

# Ensure project root in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db import get_all_sites, get_all_events, is_care_saved, toggle_saved_care
from scoring.care_access_score import calculate_care_access_score
from utils.geo import geocode_location, haversine_distance, get_directions_url
from utils.styles import inject_custom_css, render_header, LOGO_PATH


st.set_page_config(
    page_title="Find Free & Low-Cost Care | CareAtZero",
    page_icon=LOGO_PATH,
    layout="wide"
)

inject_custom_css()
render_header("find_care")

# Header
st.markdown("""
<div style="margin-bottom: 20px;">
    <h2 style="margin: 0; color: #1E293B;">🔍 Find Free or Low-Cost Care</h2>
    <p style="margin: 4px 0 0 0; color: #64748B;">Search verified free clinics, sliding-scale safety net centers, and upcoming mobile pop-ups.</p>
</div>
""", unsafe_allow_html=True)

# Retrieve preset filters from session state if coming from Home page
default_service = st.session_state.get("selected_service", "Dental")
default_loc = st.session_state.get("search_loc", "27514")
default_timing = st.session_state.get("search_timing", "This Week")

# --- FILTER SECTION ---
with st.container():
    st.markdown("#### 1. Search Criteria")
    col1, col2, col3 = st.columns([1.5, 1.2, 1.2])

    with col1:
        service_options = ["Dental", "Medical", "Vision", "Behavioral Health"]
        s_idx = service_options.index(default_service) if default_service in service_options else 0
        service_needed = st.selectbox("🩺 **Service Needed** *", service_options, index=s_idx)

    with col2:
        location_input = st.text_input("📍 **Your Location (ZIP or City)** *", value=default_loc, help="Enter a 5-digit ZIP code (e.g. 27514, 27601, 27701) or NC city")

    with col3:
        timing_options = ["This Week", "Today", "Flexible (Upcoming)"]
        t_idx = timing_options.index(default_timing) if default_timing in timing_options else 0
        timing_pref = st.selectbox("⏱️ **When Care is Needed**", timing_options, index=t_idx)

    with st.expander("⚙️ **Optional Filters & Eligibility Tuning (Click to expand)**", expanded=False):
        exp1, exp2, exp3, exp4 = st.columns(4)
        with exp1:
            age_group = st.selectbox("👤 **Age Group**", ["Adults (18-64)", "Children & Youth (0-17)", "Seniors (65+)", "All Ages"])
        with exp2:
            insurance_status = st.selectbox("🛡️ **Insurance Status**", ["Uninsured", "Underinsured / High Deductible", "Prefer not to say"])
        with exp3:
            income_band = st.selectbox("💵 **Household Income**", ["Under $25,000 / $0", "$25,000 - $45,000", "$45,000+", "Prefer not to say"], help="Used only to estimate sliding-scale fee tier.")
        with exp4:
            cost_filter = st.selectbox("🏷️ **Cost Preference**", ["All Low-Cost & Free", "Free Only ($0 Fee)", "Free & Very Low Cost", "Sliding Scale Included"])

        col_dist, col_sort = st.columns(2)
        with col_dist:
            max_dist = st.slider("🚗 **Maximum Distance (miles)**", min_value=5, max_value=60, value=35, step=5)
        with col_sort:
            sort_by = st.radio("📊 **Sort Results By**", ["Care Access Score (Best realistic match)", "Closest Distance"], horizontal=True)

# Geocode location
user_lat, user_lon, loc_label = geocode_location(location_input)

# Fetch data from SQLite
sites = get_all_sites()
events = get_all_events(include_expired=False, current_date_str="2026-09-16")
all_records = sites + events

# Filter and score records
scored_records = []
current_date_ref = "2026-09-16"

for rec in all_records:
    # 1. Service Filter Check
    services = rec.get("services", [])
    service_match = any(service_needed.lower() in s.lower() for s in services)
    if not service_match:
        continue

    # 2. Cost Filter Check
    cost_class = rec.get("cost_class", "Sliding Scale")
    if cost_filter == "Free Only ($0 Fee)" and cost_class != "Free":
        continue
    elif cost_filter == "Free & Very Low Cost" and cost_class not in ["Free", "Very Low Cost"]:
        continue

    # 3. Calculate distance
    rec_lat = rec.get("latitude")
    rec_lon = rec.get("longitude")
    dist = haversine_distance(user_lat, user_lon, rec_lat, rec_lon) if rec_lat and rec_lon else 12.0

    if dist > max_dist:
        continue

    # 4. Calculate 100-point Care Access Score
    score, breakdown, reasons = calculate_care_access_score(
        record=rec,
        service_needed=service_needed,
        distance_miles=dist,
        timing_pref=timing_pref,
        user_insurance=insurance_status if 'insurance_status' in locals() else "Uninsured",
        user_income_band=income_band if 'income_band' in locals() else "Under $25k",
        reference_date_str=current_date_ref
    )

    rec_entry = {
        "record": rec,
        "distance": dist,
        "score": score,
        "breakdown": breakdown,
        "reasons": reasons
    }
    scored_records.append(rec_entry)

# Sort records
if 'sort_by' in locals() and "Closest Distance" in sort_by:
    scored_records.sort(key=lambda x: x["distance"])
else:
    scored_records.sort(key=lambda x: (x["score"], -x["distance"]), reverse=True)

st.markdown("---")

# Results Header
res_col1, res_col2 = st.columns([3, 1])
with res_col1:
    st.markdown(f"### Results for **{service_needed} Care** near **{loc_label}** ({len(scored_records)} options found)")
with res_col2:
    view_mode = st.radio("View as:", ["📋 List View", "🗺️ Map View"], horizontal=True, label_visibility="collapsed")

# Map View Rendering
if view_mode == "🗺️ Map View":
    st.markdown("#### 🗺️ Interactive Clinic & Pop-Up Event Map")
    m = folium.Map(location=[user_lat, user_lon], zoom_start=10, tiles="CartoDB positron")

    # User search location marker
    folium.Marker(
        [user_lat, user_lon],
        popup=f"Your Location: {loc_label}",
        tooltip="Your Location",
        icon=folium.Icon(color="red", icon="user", prefix="fa")
    ).add_to(m)

    # Provider markers
    for item in scored_records:
        rec = item["record"]
        lat = rec.get("latitude")
        lon = rec.get("longitude")
        if not lat or not lon:
            continue

        cost = rec.get("cost_class", "Sliding Scale")
        is_evt = rec.get("record_type") == "event"
        title = rec.get("title") or rec.get("name")

        color = "green" if cost == "Free" else ("blue" if cost == "Sliding Scale" else "orange")
        icon_name = "calendar" if is_evt else "plus-square"

        popup_html = f"""
        <b>{title}</b><br/>
        Cost: <b>{cost}</b><br/>
        Score: <b>{item['score']}/100</b><br/>
        Distance: {item['distance']} mi<br/>
        Phone: {rec.get('phone', 'N/A')}
        """

        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"[{cost}] {title} ({item['distance']} mi)",
            icon=folium.Icon(color=color, icon=icon_name, prefix="fa")
        ).add_to(m)

    st_folium(m, width=None, height=450)
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# List View of Results
if not scored_records:
    st.warning(f"No {service_needed} care options found within {max_dist} miles of {loc_label} matching your criteria. Try expanding the distance slider or choosing 'All Low-Cost & Free'.")
else:
    for idx, item in enumerate(scored_records):
        rec = item["record"]
        score = item["score"]
        dist = item["distance"]
        reasons = item["reasons"]

        is_event = rec.get("record_type") == "event"
        title = rec.get("title") or rec.get("name")
        cost_class = rec.get("cost_class", "Sliding Scale")

        # Badge styling
        if cost_class == "Free":
            cost_badge = "<span class='badge-free'>FREE ($0)</span>"
        elif cost_class == "Very Low Cost":
            cost_badge = "<span class='badge-lowcost'>VERY LOW COST</span>"
        else:
            cost_badge = "<span class='badge-sliding'>SLIDING SCALE</span>"

        type_badge = "<span class='badge-event'>🚐 POP-UP EVENT</span>" if is_event else "<span class='badge-lowcost'>🏥 PERMANENT CLINIC</span>"

        timing_text = f"📅 Event Date: <strong>{rec.get('date_start')}</strong> ({rec.get('time_details')})" if is_event else f"⏰ Hours: {rec.get('hours_summary')}"
        appt_text = f"📋 Rule: {rec.get('appointment_rule')}"
        docs_text = f"📄 What to bring: {', '.join(rec.get('documents_required', ['Photo ID']))}"

        # Render custom styled care card
        card_html = f"""
        <div class="care-card">
            <div class="care-card-header">
                <div>
                    {cost_badge} {type_badge}
                    <h3 class="care-card-title" style="margin-top: 6px;">{title}</h3>
                </div>
                <div class="score-badge">
                    ⭐ Care Access Score: <strong>{score}/100</strong>
                </div>
            </div>
            <div class="card-meta">📍 <strong>{rec.get('address')}, {rec.get('city')}, NC</strong> • <span style="color:#2563EB; font-weight:600;">{dist} miles away</span></div>
            <div class="card-meta">🩺 <strong>Services:</strong> {', '.join(rec.get('services', []))}</div>
            <div class="card-meta">{timing_text}</div>
            <div class="card-meta">{appt_text}</div>
            <div class="card-meta">{docs_text}</div>
            <div class="reasons-box">
                <strong>Why this matches:</strong>
                <ul>
                    {''.join([f'<li>{r}</li>' for r in reasons[:3]])}
                </ul>
            </div>
            <div class="source-meta">
                Source: {rec.get('source_name', 'Verified Safety Net Directory')} • Last checked: {rec.get('last_checked', 'Recently verified')}
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

        # Action Buttons Row
        btn_c1, btn_c2, btn_c3 = st.columns([1.5, 1, 1])

        with btn_c1:
            if st.button(f"📋 View Full Details", key=f"btn_det_{rec.get('id')}_{idx}", type="primary", use_container_width=True):
                st.session_state["selected_care_id"] = rec.get("id")
                st.session_state["selected_care_type"] = rec.get("record_type")
                st.switch_page("pages/2_📋_Care_Details.py")

        with btn_c2:
            phone_num = rec.get("phone", "")
            if phone_num:
                clean_phone = phone_num.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
                st.link_button(f"📞 Call", f"tel:{clean_phone}", use_container_width=True)
            else:
                st.button("📞 Call", disabled=True, key=f"call_dis_{idx}", use_container_width=True)

        with btn_c3:
            addr = f"{rec.get('address')}, {rec.get('city')}, NC"
            maps_url = get_directions_url(addr, rec.get("latitude"), rec.get("longitude"))
            st.link_button(f"🗺️ Directions", maps_url, use_container_width=True)

        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)



