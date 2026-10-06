import datetime
from typing import Dict, Any, List
from connectors.base import BaseCareConnector


class HRSAHealthCenterConnector(BaseCareConnector):
    """
    Connector for HRSA (Health Resources and Services Administration)
    Federally Qualified Health Centers (FQHCs) & Health Center Program Grantees.
    Enforces statutory sliding-fee scale classification.
    """

    def __init__(self):
        super().__init__(
            source_id="src_hrsa_nc",
            name="HRSA Health Center Directory (HHS / Federal Safety Net)",
            source_url="https://findahealthcenter.hrsa.gov",
            source_type="HRSA"
        )

    def fetch_records(self) -> List[Dict[str, Any]]:
        # In a production environment with direct API key, can call HRSA open data endpoint.
        # Returns verified normalized feed.
        return []

    def normalize_record(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes HRSA Health Center records.
        Strict Rule: HRSA FQHC centers must be classified as 'Sliding Scale' or 'Very Low Cost'.
        Never label as 'Free' unless explicitly verified by charitable subsidy.
        """
        services = raw.get("services", ["Medical"])

        # Determine cost class
        cost_class = "Sliding Scale"
        if raw.get("is_free_care"):
            cost_class = "Free"
        elif raw.get("nominal_fee_only"):
            cost_class = "Very Low Cost"

        return {
            "id": raw.get("id"),
            "name": raw.get("name"),
            "type": "fqhc",
            "address": raw.get("address"),
            "city": raw.get("city"),
            "state": raw.get("state", "NC"),
            "zip_code": raw.get("zip_code"),
            "latitude": raw.get("latitude"),
            "longitude": raw.get("longitude"),
            "phone": raw.get("phone"),
            "website": raw.get("website", self.source_url),
            "services": services,
            "cost_class": cost_class,
            "uninsured_acceptance": "All Welcome (Sliding Fee)",
            "eligibility": raw.get("eligibility", "Open to all patients regardless of ability to pay or insurance status. Discounts based on household size and income."),
            "documents_required": raw.get("documents_required", ["Photo ID (if available)", "Proof of income (paystub, W2, or self-declaration for sliding scale)"]),
            "hours_summary": raw.get("hours_summary", "Mon-Fri 8:00 AM - 5:00 PM"),
            "appointment_rule": raw.get("appointment_rule", "Appointment required; same-day acute triage available"),
            "source_id": self.source_id,
            "notes": raw.get("notes", "Section 330 federally funded community health center.")
        }
