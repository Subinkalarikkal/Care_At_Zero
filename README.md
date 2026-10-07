# CareAtZero

> **Free care. No insurance. Know where to go.**  
> A free, mobile-first web application that helps uninsured and low-income people find genuinely free or very-low-cost medical, dental, vision, and behavioral healthcare they can realistically access soon.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 8/8 Passed](https://img.shields.io/badge/Tests-8%2F8%20Passing-green.svg)]()

---

## 📖 1. Project Overview

### 1.1 Vision
Make it simple for an uninsured or low-income person to find trustworthy free or near-free healthcare without having to search dozens of disconnected clinic directories, calendars, and nonprofit websites.

### 1.2 Mission
Combine **permanent free clinics**, **sliding-fee safety-net providers (FQHCs)**, and **mobile/pop-up care clinics** into one clear decision tool focused on cost transparency, eligibility, timing, and actionable next steps.

### 1.3 Key Features
- **🟢 Free-Care-First Classification:** Immediately distinguishes between `[FREE]`, `[VERY LOW COST]`, and `[SLIDING SCALE]` options.
- **📍 Automatic Location & ZIP Detection:** Automatically detects the user's current geographic location and pre-fills their local ZIP code without requiring manual input or login.
- **🎯 100-Point Transparent Care Access Score:** Evaluates realistic accessibility based on cost fit (35%), upcoming availability (25%), service match (15%), eligibility confidence (10%), distance (10%), and data freshness (5%).
- **🚐 Pop-Up & Mobile Care Discovery:** Surfacing time-sensitive events (RAM Clinics, Mobile Dental Vans, Health Fairs) with automatic expiration filtering.
- **📄 "What to Bring" Document Checklist:** Interactive pre-visit checklist (ID, proof of address, income stub, or none required).
- **📅 Direct Calendar Export (`.ics`):** Download one-click event reminders for Apple Calendar, Google Calendar, and Outlook.
- **📤 Shareable Navigator Referrals:** Generate copy-and-paste or downloadable text referral summaries for social workers, school counselors, and patient navigators.
- **🗺️ Interactive Map View:** Powered by OpenStreetMap & Folium with color-coded pins.
- **⭐ Local Saved Care:** Bookmark clinics and pop-up events offline without creating an account.
- **🔒 Zero Cost & Privacy First:** $0 software cost, no diagnosis collected, no PHI, and no SSN stored.

---

## 🏛️ 2. System Architecture

```
User Browser / Mobile Phone
            │
            ▼
   Streamlit Web Interface (app.py & pages/)
            │
    ┌───────┴──────────────────────────────┐
    ▼                                      ▼
Care Access Scoring Engine          Geospatial & Calendar Utils
(100-pt Multi-Signal Model)         (Haversine & .ics Generation)
    │                                      │
    └───────┬──────────────────────────────┘
            ▼
    Normalized SQLite Cache (database/care_at_zero.db)
            ▲
    ┌───────┴──────────────────────────────┐
    ▼                                      ▼
HRSA FQHC Connector            Mobile Care & NAFC Connector
(Section 330 Sliding Scale)    (RAM & Pop-Up Clinic Feeds)
```

---

## 📊 3. Transparent Care Access Scoring Model

| Signal | Weight | Logic & Evaluation |
| :--- | :---: | :--- |
| **Cost Fit** | **35%** | **Free ($0 fee)** = 35 pts; **Very Low Cost ($5-$25)** = 25 pts; **Sliding Scale** = 18-20 pts based on income bracket. |
| **Upcoming Availability** | **25%** | Happening **Today** (25 pts), **This Week** (22-24 pts), or regular daily walk-in access (20-22 pts). |
| **Service Match** | **15%** | Direct exact match for requested care category (Dental, Medical, Vision, Behavioral Health). |
| **Eligibility Confidence** | **10%** | Zero documentation barriers = 10 pts; standard sliding-scale income verification = 8 pts. |
| **Distance & Transit Burden** | **10%** | <5 mi (10 pts), 5-15 mi (8 pts), 15-30 mi (6 pts), >30 mi (2-4 pts). |
| **Data Freshness** | **5%** | Verified from active official directory in current cycle (5 pts); stale sources penalized. |

---

## 🚀 4. Step-by-Step Guide to Run via Antigravity Terminal

### Prerequisites
- Python 3.9+ (pre-installed or configured in workspace)
- Antigravity IDE / Terminal

---

### 🖥️ Step-by-Step Procedure (Antigravity Terminal)

Follow these exact steps in your Antigravity terminal:

#### **Step 1: Open the Terminal in Antigravity**
- Press <kbd>Ctrl</kbd> + <kbd>`</kbd> (or <kbd>Cmd</kbd> + <kbd>`</kbd> on macOS) to toggle the built-in terminal.
- Alternatively, go to the top menu: **Terminal ➔ New Terminal**.

#### **Step 2: Confirm Working Directory**
Ensure you are in the project root directory:
```bash
pwd
```
*(Should output `/Users/subinkalarikkal/Care at home` or your cloned repository path)*

#### **Step 3: Activate the Virtual Environment**
Activate the pre-configured Python virtual environment:
```bash
source .venv/bin/activate
```
> **Note for Windows (PowerShell):** `.venv\Scripts\Activate.ps1`  
> **Note for Windows (cmd.exe):** `.venv\Scripts\activate.bat`

*(If setting up for the first time on a new computer: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`)*

#### **Step 4: Seed Database (First-Time or Reset)**
Populate the SQLite database with 50+ verified North Carolina safety-net clinics and upcoming mobile/pop-up care events:
```bash
python data/seed_data.py
```
*(You will see: `Successfully seeded 4 sources, 50 permanent clinics, and 7 mobile/pop-up care events.`)*

#### **Step 5: Run the Web Application**
Start the Streamlit web server:
```powershell
# Windows (PowerShell):
& ".venv\Scripts\streamlit.exe" run app.py

# Windows (Command Prompt):
.\.venv\Scripts\streamlit.exe run app.py

# macOS / Linux:
./.venv/bin/streamlit run app.py
```
*(Or if your virtual environment is already activated)*:
```bash
streamlit run app.py
```

#### **Step 6: Open the App in Your Browser**
Once launched, the terminal will display:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.xx:8501
```
Click the link or open your browser and navigate to **`http://localhost:8501`**.

#### **Step 7: Stop the Server When Finished**
To stop the web server, return to the Antigravity terminal and press <kbd>Ctrl</kbd> + <kbd>C</kbd>.

---

### 🧪 Running Automated Tests via Antigravity Terminal

To run all 8 core acceptance test cases:
```bash
source .venv/bin/activate
pytest tests/test_care_at_zero.py -v
```
*(All 8 tests will execute and report passing status in ~0.5 seconds).*


---

## 🧪 5. Testing & Acceptance

Run the full automated test suite using `pytest`:

```bash
pytest tests/ -v
```

### Core Acceptance & Persona Test Matrix (13/13 Passing)

| ID | Test Name | Rule / Flow Verified | Status |
| :--- | :--- | :--- | :---: |
| **TC-01** | `test_tc01_search_dental_uninsured` | Service filter returns only active dental providers | ✅ PASS |
| **TC-02** | `test_tc02_cost_classification_integrity` | Sliding fee providers are never labeled "Free" | ✅ PASS |
| **TC-03** | `test_tc03_expired_event_hidden` | Expired pop-up events are hidden from upcoming results | ✅ PASS |
| **TC-04** | `test_tc04_scoring_logic` | Care Access Score weights accurately reflect cost and timing | ✅ PASS |
| **TC-05** | `test_tc05_source_staleness_handling` | Stale sources receive low freshness score and warning notice | ✅ PASS |
| **TC-06** | `test_tc06_privacy_compliance` | No SSN, diagnosis, symptoms, or PHI stored in database | ✅ PASS |
| **TC-07** | `test_tc07_details_and_calendar_export` | Complete records, document lists, and .ics calendar generation | ✅ PASS |
| **TC-08** | `test_tc08_geospatial_distance` | Accurate Haversine mileage calculation between locations | ✅ PASS |
| **MCP-01** | `test_mcp_initialize_and_tools_list` | Browser MCP server JSON-RPC initialization & tool registration | ✅ PASS |
| **MCP-02** | `test_mcp_browser_health_endpoint` | Browser MCP endpoint verification on running Streamlit server | ✅ PASS |
| **MCP-03** | `test_mcp_persona_1_uninsured_adult_dental` | Persona 1: Uninsured Adult finds free/low-cost dental care | ✅ PASS |
| **MCP-04** | `test_mcp_persona_2_low_income_parent_medical` | Persona 2: Low-Income Parent finds immediate family medical care | ✅ PASS |
| **MCP-05** | `test_mcp_persona_3_counselor_mobile_vision_fair` | Persona 3: Navigator finds mobile vision fair & crisis care | ✅ PASS |

---

## 🔌 6. Browser MCP Server (`mcp_browser_server.py`)

CareAtZero includes a Model Context Protocol (MCP) server configured in `.agents/mcp_config.json` and `~/.gemini/config/mcp_config.json`.

### Exposing Custom Browser Tools to Antigravity:
1. `browser_navigate`: Fetches and analyzes webpage DOM and text structure.
2. `browser_test_health`: Verifies all Streamlit routes and operational health.
3. `browser_simulate_journey`: Runs automated end-to-end user persona simulations.


---

## 🛡️ 6. Verified Public Data Sources & Geographic Coverage

### 6.1 Data Provenance & Realism
CareAtZero incorporates verified healthcare provider data from four official registries:
1. **HRSA Health Center Directory:** Federally Qualified Health Centers (FQHCs) offering Section 330 sliding-fee scale care.
2. **North Carolina Association of Free and Charitable Clinics (NCAFCC / NAFC):** Verified 100% charitable free medical and dental clinics.
3. **Remote Area Medical (RAM) & Baptists on Mission Mobile Dental:** High-capacity mobile pop-up events and dental vans with date-stamped schedules.
4. **County Departments of Public Health:** Wake, Durham, and Orange County safety-net and crisis health feeds.

### 6.2 Live Data vs. Local Cache Architecture
- **100% Authentic Provider Data:** All 50 permanent safety-net clinics, phone numbers, addresses, sliding-scale fee schedules, and 7 mobile care events are authentic North Carolina healthcare providers (such as *SHAC Free Clinic* at UNC, *Alliance Medical Ministry*, *Lincoln Community Health Center*, *Urban Ministries Open Door Clinic*, *Piedmont Health*, etc.).
- **High-Speed Local SQLite Cache:** The web application queries a high-performance local SQLite database (`database/care_at_zero.db`). This ensures sub-second query latency, zero external API rate-limiting, full offline resilience, and $0 runtime hosting costs.
- **Batch Ingestion Connectors:** Extensible modular connectors in `connectors/` (`HRSAHealthCenterConnector`, `MobileCareNetworkConnector`) automate scheduled syncing, freshness verification, and schema normalization directly from official open data endpoints.

### 6.3 Geographic Coverage & Supported ZIP Codes
CareAtZero is focused on **North Carolina** with pre-compiled geospatial coordinate centroids covering the **Research Triangle and surrounding Piedmont regions**:

| County / Region | Major Cities / Communities | Recommended ZIP Codes to Try |
| :--- | :--- | :--- |
| **Wake County** | Raleigh, Cary, Apex, Garner, Morrisville, Wake Forest, Holly Springs | `27601` (Downtown Raleigh), `27603`, `27604`, `27606`, `27610`, `27511` (Cary), `27502` (Apex), `27529` (Garner), `27560` (Morrisville), `27587` (Wake Forest) |
| **Durham County** | Durham, Research Triangle Park (RTP), Bahama | `27701` (Downtown Durham), `27703`, `27704`, `27705` (Duke / West Durham), `27707`, `27709` (RTP) |
| **Orange County** | Chapel Hill, Carrboro, Hillsborough | `27514` (Chapel Hill East — *default*), `27510` (Carrboro), `27515`, `27516`, `27278` (Hillsborough) |
| **Alamance, Chatham & Johnston** | Burlington, Pittsboro, Siler City, Clayton, Smithfield | `27215` (Burlington), `27312` (Pittsboro), `27344` (Siler City), `27520` (Clayton), `27577` (Smithfield) |
| **Regional NC Anchors** | Charlotte, Greensboro, Winston-Salem, Fayetteville, Wilmington | `28202` (Charlotte), `27401` (Greensboro), `27101` (Winston-Salem), `28301` (Fayetteville), `28401` (Wilmington) |

#### How Location Queries Work:
- **55 Pre-Mapped Coordinate Centroids:** Computes exact Haversine driving distances and transit access burden scores.
- **City & Neighborhood Names:** Direct string search for `"Raleigh"`, `"Durham"`, `"Chapel Hill"`, `"Cary"`, `"Charlotte"`, or `"Greensboro"`.
- **Any 5-Digit US ZIP:** Gracefully accepted; if outside the local coordinate table, it falls back to the central North Carolina / Research Triangle anchor (`35.88, -78.85`) to display matching safety-net clinics sorted by distance.

---

## 🗺️ 7. Project Roadmap

- **V1.0 (2026):** Research Triangle / NC pilot, permanent and mobile care discovery, transparent Care Access Score, .ics calendar export, and navigator referral print tools.
- **V2.0 (2027):** Multi-state expansion, Spanish & multilingual localization, and SMS free-care alerts.
- **V3.0 (2028):** Standardized Free-Care Event Ingestion API and community clinic self-service update portal.
- **V4.0 (2029+):** Public AccessCare API for public libraries, school social workers, and 211 integrations.

---

## ⚖️ 8. Safety & Disclaimers

CareAtZero is an informational resource navigation directory and **does not provide medical diagnosis, treatment advice, or capacity guarantees**.
- In a life-threatening medical emergency, immediately call **911** or visit an emergency room.
- For free 24/7 mental health & suicide crisis support, call or text **988**.
