import streamlit as st
import os
import sys

# Ensure project root in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db import get_all_saved_care


def inject_custom_css():
    """Injects high-quality, mobile-first responsive PWA CSS styling into Streamlit."""
    st.markdown("""
    <style>
    /* Global styles and modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        -webkit-tap-highlight-color: transparent;
        -webkit-touch-callout: none;
    }

    /* Fix Streamlit Header & Mobile Top Clearance */
    header[data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.90) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        z-index: 99 !important;
    }

    /* Container Padding with Full Top Clearance */
    .block-container {
        padding-top: 4.8rem !important;
        padding-bottom: 6.5rem !important;
        padding-left: 1.0rem !important;
        padding-right: 1.0rem !important;
        max-width: 900px;
    }


    /* Hide default Streamlit multi-page sidebar on small screens to give full mobile app feel */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        button[data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
    }

    /* Top Mobile App Bar */
    .mobile-app-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .app-brand-badge {
        display: flex;
        align-items: center;
        gap: 6px;
        font-weight: 800;
        font-size: 1.05rem;
        color: #1E40AF;
        text-decoration: none;
    }

    /* Top Emergency Alert Bar */
    .emergency-banner {
        background-color: #FEF2F2;
        border: 1px solid #FCA5A5;
        border-left: 4px solid #EF4444;
        border-radius: 10px;
        padding: 10px 14px;
        margin-top: 0px;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 0.84rem;
        color: #991B1B;
        line-height: 1.4;
    }
    .emergency-banner strong {
        color: #7F1D1D;
    }


    /* Main Brand Hero */
    .brand-hero {
        background: linear-gradient(135deg, #1E40AF 0%, #2563EB 60%, #3B82F6 100%);
        color: white;
        padding: 20px 16px;
        border-radius: 16px;
        margin-bottom: 12px;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.20);
    }
    .brand-title {
        font-size: 1.65rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        color: #FFFFFF !important;
    }
    .brand-subtitle {
        font-size: 0.92rem;
        opacity: 0.95;
        margin-top: 5px;
        margin-bottom: 0;
        color: #EFF6FF !important;
        line-height: 1.35;
    }

    /* Badges */
    .badge-free {
        display: inline-block;
        background-color: #DCFCE7;
        color: #15803D;
        border: 1px solid #86EFAC;
        padding: 3px 9px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-lowcost {
        display: inline-block;
        background-color: #E0F2FE;
        color: #0369A1;
        border: 1px solid #7DD3FC;
        padding: 3px 9px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-sliding {
        display: inline-block;
        background-color: #EDE9FE;
        color: #6D28D9;
        border: 1px solid #C4B5FD;
        padding: 3px 9px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-event {
        display: inline-block;
        background-color: #FEF3C7;
        color: #B45309;
        border: 1px solid #FCD34D;
        padding: 3px 9px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* Care Result Card - Mobile Optimized */
    .care-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .care-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.07);
    }
    .care-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
        flex-wrap: wrap;
        gap: 6px;
    }
    .care-card-title {
        font-size: 1.10rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
        line-height: 1.3;
    }
    .score-badge {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        padding: 3px 9px;
        border-radius: 8px;
        font-size: 0.80rem;
        font-weight: 700;
        color: #15803D;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .card-meta {
        font-size: 0.82rem;
        color: #475569;
        margin: 4px 0;
        display: flex;
        align-items: flex-start;
        gap: 6px;
        line-height: 1.35;
    }
    .reasons-box {
        background-color: #F8FAFC;
        border-left: 3px solid #3B82F6;
        padding: 8px 10px;
        border-radius: 0 8px 8px 0;
        margin-top: 8px;
        font-size: 0.78rem;
        color: #334155;
    }
    .reasons-box ul {
        margin: 3px 0 0 0;
        padding-left: 15px;
    }
    .source-meta {
        font-size: 0.72rem;
        color: #94A3B8;
        margin-top: 6px;
    }

    /* Stats Box on Home */
    .stat-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 12px 8px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .stat-number {
        font-size: 1.45rem;
        font-weight: 800;
        color: #2563EB;
        margin: 0;
    }
    .stat-label {
        font-size: 0.70rem;
        font-weight: 600;
        color: #64748B;
        margin-top: 2px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    /* Trust Pill */
    .trust-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: #F1F5F9;
        color: #334155;
        padding: 3px 9px;
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 600;
    }

    /* Standard Button Styling */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.90rem !important;
        min-height: 44px !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:active {
        transform: scale(0.97);
    }

    /* TOP NAVIGATION BAR (Header Navigation) */
    div[data-testid="stHorizontalBlock"]:has(button[key^="topnav_"]) {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        padding: 6px 8px !important;
        margin-top: 0px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
    }

    div[data-testid="stHorizontalBlock"]:has(button[key^="topnav_"]) div[data-testid="column"] {
        flex: 1 1 0 !important;
        min-width: 0 !important;
        padding: 0 2px !important;
        margin: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(button[key^="topnav_"]) button {
        min-height: 42px !important;
        height: 42px !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        line-height: 1.2 !important;
        padding: 4px 6px !important;
        border-radius: 10px !important;
        white-space: nowrap !important;
    }

    /* FIXED MOBILE BOTTOM NAVIGATION DOCK (Native Streamlit Buttons Pinned) */
    div[data-testid="stHorizontalBlock"]:has(button[key^="dock_"]) {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999999 !important;
        background: rgba(255, 255, 255, 0.96) !important;
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;
        border-top: 1px solid #CBD5E1 !important;
        box-shadow: 0 -4px 18px rgba(0, 0, 0, 0.10) !important;
        padding: 6px 8px calc(8px + env(safe-area-inset-bottom, 0px)) 8px !important;
        margin: 0 !important;
        display: flex !important;
        justify-content: space-around !important;
    }

    div[data-testid="stHorizontalBlock"]:has(button[key^="dock_"]) div[data-testid="column"] {
        flex: 1 1 0 !important;
        min-width: 0 !important;
        padding: 0 2px !important;
        margin: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(button[key^="dock_"]) button {
        min-height: 48px !important;
        height: 48px !important;
        font-size: 0.72rem !important;
        line-height: 1.15 !important;
        padding: 2px 2px !important;
        border-radius: 8px !important;
        white-space: pre-line !important;
    }

    /* Mobile view optimizations */
    @media (max-width: 640px) {
        .brand-title {
            font-size: 1.35rem !important;
        }
        .brand-hero {
            padding: 16px 12px !important;
            border-radius: 12px !important;
        }
        .care-card {
            padding: 12px !important;
            border-radius: 12px !important;
        }
        .stat-number {
            font-size: 1.25rem !important;
        }
        div[data-testid="stHorizontalBlock"]:has(button[key^="topnav_"]) button {
            font-size: 0.75rem !important;
            padding: 2px 4px !important;
            min-height: 38px !important;
            height: 38px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def render_brand_header():
    """Renders the top CareAtZero brand hero banner."""
    st.markdown("""
    <div class="brand-hero">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div>
                <h1 class="brand-title">CareAtZero 🩺</h1>
                <p class="brand-subtitle">Find genuinely free, very-low-cost, and sliding-scale healthcare you can realistically access soon.</p>
            </div>
            <div>
                <span class="trust-pill" style="background: rgba(255,255,255,0.2); color: #fff;">
                    ✓ 100% Free & Open Access
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_emergency_banner():
    """Renders persistent emergency guidance at top of application."""
    st.markdown("""
    <div class="emergency-banner">
        <div>
            🚨 <strong>Medical Emergency?</strong> If experiencing a life-threatening emergency, call <strong>911</strong>. For free 24/7 mental health & suicide crisis support, dial <strong>988</strong>.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_header(active_page: str = "home"):
    """
    Renders the unified top section across all pages:
    1. CareAtZero Hero Banner
    2. Navigation Bar (Home, Find, Detail, Saved, About)
    3. Medical Emergency Warning Banner
    """
    render_brand_header()
    render_top_nav(active_page)
    render_emergency_banner()


def render_top_nav(active_page: str = "home"):
    """
    Renders top navigation bar across all pages with active state highlighting
    and live saved count badge.
    """
    try:
        saved_items = get_all_saved_care()
        saved_count = len(saved_items)
    except Exception:
        saved_count = 0

    b1, b2, b3, b4, b5 = st.columns(5)
    with b1:
        if st.button("🏠 Home", key="topnav_home", use_container_width=True, type="primary" if active_page == "home" else "secondary"):
            if active_page != "home":
                st.switch_page("app.py")

    with b2:
        if st.button("🔍 Find", key="topnav_find", use_container_width=True, type="primary" if active_page == "find_care" else "secondary"):
            if active_page != "find_care":
                st.switch_page("pages/1_🔍_Find_Free_Care.py")

    with b3:
        if st.button("📋 Detail", key="topnav_detail", use_container_width=True, type="primary" if active_page == "details" else "secondary"):
            if active_page != "details":
                st.switch_page("pages/2_📋_Care_Details.py")

    with b4:
        saved_lbl = f"⭐ Saved ({saved_count})" if saved_count > 0 else "⭐ Saved"
        if st.button(saved_lbl, key="topnav_saved", use_container_width=True, type="primary" if active_page == "saved" else "secondary"):
            if active_page != "saved":
                st.switch_page("pages/3_⭐_Saved_Care.py")

    with b5:
        if st.button("ℹ️ About", key="topnav_about", use_container_width=True, type="primary" if active_page == "about" else "secondary"):
            if active_page != "about":
                st.switch_page("pages/4_ℹ️_About_&_Safety.py")


def render_bottom_nav(active_page: str = "home"):
    """
    Renders the fixed PWA bottom navigation bar on mobile viewports
    with active tab styling and saved count badge.
    """
    try:
        saved_items = get_all_saved_care()
        saved_count = len(saved_items)
    except Exception:
        saved_count = 0

    st.markdown("<div style='margin-bottom: 70px;'></div>", unsafe_allow_html=True)

    b1, b2, b3, b4, b5 = st.columns(5)
    with b1:
        if st.button("🏠\nHome", key="dock_home", use_container_width=True, type="primary" if active_page == "home" else "secondary"):
            if active_page != "home":
                st.switch_page("app.py")

    with b2:
        if st.button("🔍\nFind", key="dock_find", use_container_width=True, type="primary" if active_page == "find_care" else "secondary"):
            if active_page != "find_care":
                st.switch_page("pages/1_🔍_Find_Free_Care.py")

    with b3:
        if st.button("📋\nDetail", key="dock_detail", use_container_width=True, type="primary" if active_page == "details" else "secondary"):
            if active_page != "details":
                st.switch_page("pages/2_📋_Care_Details.py")

    with b4:
        saved_lbl = f"⭐\nSaved ({saved_count})" if saved_count > 0 else "⭐\nSaved"
        if st.button(saved_lbl, key="dock_saved", use_container_width=True, type="primary" if active_page == "saved" else "secondary"):
            if active_page != "saved":
                st.switch_page("pages/3_⭐_Saved_Care.py")

    with b5:
        if st.button("ℹ️\nAbout", key="dock_about", use_container_width=True, type="primary" if active_page == "about" else "secondary"):
            if active_page != "about":
                st.switch_page("pages/4_ℹ️_About_&_Safety.py")
