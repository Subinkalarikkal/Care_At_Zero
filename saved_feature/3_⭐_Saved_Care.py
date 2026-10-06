import streamlit as st
import os
import sys

# Ensure project root in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db import get_all_saved_care, toggle_saved_care
from utils.calendar import generate_ics_calendar
from utils.geo import get_directions_url
from utils.styles import inject_custom_css, render_header, LOGO_PATH


st.set_page_config(
    page_title="Saved Care Options | CareAtZero",
    page_icon=LOGO_PATH,
    layout="wide"
)

inject_custom_css()
render_header("saved")

st.markdown("""
<div style="margin-bottom: 20px;">
    <h2 style="margin: 0; color: #1E293B;">⭐ My Saved Care Options</h2>
    <p style="margin: 4px 0 0 0; color: #64748B;">Keep track of clinics and pop-up events you want to visit. Saved locally on your device.</p>
</div>
""", unsafe_allow_html=True)

saved_items = get_all_saved_care()

if not saved_items:
    st.info("You haven't saved any care options yet. When you search for free clinics or mobile events, click **'☆ Save Option'** to bookmark them here for quick access.")
    if st.button("🔍 Find Free Care Now", type="primary"):
        st.switch_page("pages/1_🔍_Find_Free_Care.py")
else:
    st.success(f"You have **{len(saved_items)}** saved care options bookmarked.")

    for idx, item in enumerate(saved_items):
        rec_id = item.get("id")
        rec_type = item.get("record_type")
        title = item.get("title") or item.get("name")
        cost_class = item.get("cost_class", "Sliding Scale")
        is_evt = rec_type == "event"

        cost_badge = "<span class='badge-free'>FREE</span>" if cost_class == "Free" else (
            "<span class='badge-lowcost'>VERY LOW COST</span>" if cost_class == "Very Low Cost" else "<span class='badge-sliding'>SLIDING SCALE</span>"
        )
        type_badge = "<span class='badge-event'>🚐 POP-UP EVENT</span>" if is_evt else "<span class='badge-lowcost'>🏥 CLINIC</span>"

        timing = f"📅 Date: {item.get('date_start')} ({item.get('time_details')})" if is_evt else f"⏰ Hours: {item.get('hours_summary')}"

        st.markdown(f"""
        <div class="care-card">
            <div class="care-card-header">
                <div>
                    {cost_badge} {type_badge}
                    <h3 class="care-card-title" style="margin-top: 4px;">{title}</h3>
                </div>
            </div>
            <div class="card-meta">📍 <strong>{item.get('address')}, {item.get('city')}, NC</strong></div>
            <div class="card-meta">🩺 <strong>Services:</strong> {', '.join(item.get('services', []))}</div>
            <div class="card-meta">{timing}</div>
            <div class="card-meta">📋 <strong>Rule:</strong> {item.get('appointment_rule')}</div>
            <div class="card-meta">📄 <strong>Bring:</strong> {', '.join(item.get('documents_required', ['Photo ID']))}</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])

        with c1:
            if st.button("📋 View Details", key=f"saved_det_{rec_id}_{idx}", type="primary", use_container_width=True):
                st.session_state["selected_care_id"] = rec_id
                st.session_state["selected_care_type"] = rec_type
                st.switch_page("pages/2_📋_Care_Details.py")

        with c2:
            phone_num = item.get("phone", "")
            if phone_num:
                clean_phone = phone_num.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
                st.link_button("📞 Call", f"tel:{clean_phone}", use_container_width=True)
            else:
                st.button("📞 No Phone", disabled=True, key=f"saved_nophone_{idx}", use_container_width=True)

        with c3:
            addr = f"{item.get('address')}, {item.get('city')}, NC"
            maps_url = get_directions_url(addr, item.get("latitude"), item.get("longitude"))
            st.link_button("🗺️ Directions", maps_url, use_container_width=True)

        with c4:
            if st.button("🗑️ Remove", key=f"saved_rm_{rec_id}_{idx}", use_container_width=True):
                toggle_saved_care(rec_id, rec_type)
                st.rerun()

        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)



