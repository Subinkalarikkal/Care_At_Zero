import datetime
from typing import Dict, Any, List
from connectors.base import BaseCareConnector


class MobileCareNetworkConnector(BaseCareConnector):
    """
    Connector for Mobile and Pop-Up Free Care Events (RAM Clinics, Mobile Dental Vans,
    Charitable Health Fairs, and County Health Outreach).
    """

    def __init__(self):
        super().__init__(
            source_id="src_mobile_care_nc",
            name="North Carolina Mobile & Pop-Up Care Network (RAM & Community Partners)",
            source_url="https://www.ramusa.org / https://baptistsonmission.org/medical",
            source_type="Mobile_Care_Network"
        )

    def fetch_records(self) -> List[Dict[str, Any]]:
        return []

    def is_event_active(self, event_date_end: str, current_date_str: str) -> bool:
        """TC-03: Strictly tests if an event is active or expired."""
        try:
            evt_dt = datetime.date.fromisoformat(event_date_end)
            curr_dt = datetime.date.fromisoformat(current_date_str)
            return evt_dt >= curr_dt
        except Exception:
            return True

    def normalize_record(self, raw: Dict[str, Any], current_date_str: str = "2026-09-16") -> Dict[str, Any]:
        """
        Normalizes mobile care events and computes active status.
        """
        is_active = 1 if self.is_event_active(raw.get("date_end", raw.get("date_start", "")), current_date_str) else 0

        return {
            "id": raw.get("id"),
            "title": raw.get("title"),
            "provider_id": raw.get("provider_id"),
            "organizer_name": raw.get("organizer_name"),
            "date_start": raw.get("date_start"),
            "date_end": raw.get("date_end", raw.get("date_start")),
            "time_details": raw.get("time_details", "Gates open at 6:00 AM; Clinic begins at 8:00 AM"),
            "recurring_rule": raw.get("recurring_rule"),
            "location_name": raw.get("location_name"),
            "address": raw.get("address"),
            "city": raw.get("city"),
            "state": raw.get("state", "NC"),
            "zip_code": raw.get("zip_code"),
            "latitude": raw.get("latitude"),
            "longitude": raw.get("longitude"),
            "services": raw.get("services", ["Dental", "Vision", "Medical"]),
            "cost_class": raw.get("cost_class", "Free"),
            "eligibility": raw.get("eligibility", "No ID, insurance, or proof of income required. First come, first served."),
            "appointment_rule": raw.get("appointment_rule", "No appointment needed; arrive early for numbered intake ticket"),
            "documents_required": raw.get("documents_required", ["None required (bring medication list if taking prescription drugs)"]),
            "phone": raw.get("phone", ""),
            "source_id": self.source_id,
            "is_active": is_active
        }
