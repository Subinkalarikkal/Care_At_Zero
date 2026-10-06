import datetime
from typing import Dict, Any


def generate_ics_calendar(event: Dict[str, Any]) -> str:
    """
    Generates standard RFC 5545 iCalendar (.ics) string for a mobile care event or clinic visit.
    Can be directly downloaded and imported into Google Calendar, Apple Calendar, Outlook, etc.
    """
    title = event.get("title") or event.get("name", "CareAtZero Health Appointment")
    location = f"{event.get('address', '')}, {event.get('city', '')}, {event.get('state', '')} {event.get('zip_code', '')}".strip(" ,")
    organizer = event.get("organizer_name") or event.get("name", "CareAtZero Safety Net Care")
    cost_class = event.get("cost_class", "Free")
    phone = event.get("phone", "N/A")
    website = event.get("source_url") or event.get("website", "https://careatzero.org")

    # Format dates
    date_start_str = event.get("date_start") or datetime.date.today().isoformat()
    date_end_str = event.get("date_end") or date_start_str

    try:
        dt_start = datetime.date.fromisoformat(date_start_str)
        dt_end = datetime.date.fromisoformat(date_end_str)
    except Exception:
        dt_start = datetime.date.today()
        dt_end = dt_start

    # Format times
    start_fmt = dt_start.strftime("%Y%m%d") + "T080000"
    end_fmt = dt_end.strftime("%Y%m%d") + "T160000"
    now_stamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    uid = f"careatzero-{event.get('id', 'evt')}-{start_fmt}@careatzero.org"

    docs = ", ".join(event.get("documents_required", ["Photo ID (if available)"]))
    services = ", ".join(event.get("services", ["Medical/Dental/Vision"]))
    appt_rule = event.get("appointment_rule", "First come, first served")

    description = (
        f"CareAtZero Free/Low-Cost Care Event\\n\\n"
        f"Cost: {cost_class}\\n"
        f"Services: {services}\\n"
        f"Appointment Rule: {appt_rule}\\n"
        f"What to bring: {docs}\\n"
        f"Contact Phone: {phone}\\n"
        f"Official Source: {website}\\n\\n"
        f"Important: Arrive early for walk-in/pop-up care clinics."
    )

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CareAtZero//SafetyNet Health Discovery//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{now_stamp}
DTSTART:{start_fmt}
DTEND:{end_fmt}
SUMMARY:[{cost_class}] {title}
LOCATION:{location}
DESCRIPTION:{description}
ORGANIZER;CN={organizer}:mailto:info@careatzero.org
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT
END:VCALENDAR"""

    return ics_content.strip()
