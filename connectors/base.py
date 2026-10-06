from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseCareConnector(ABC):
    """
    Base class for all safety net healthcare public data connectors.
    Provides standard methods for ingestion, normalization, freshness validation,
    and graceful error handling.
    """

    def __init__(self, source_id: str, name: str, source_url: str, source_type: str):
        self.source_id = source_id
        self.name = name
        self.source_url = source_url
        self.source_type = source_type
        self.status = "active"

    @abstractmethod
    def fetch_records(self) -> List[Dict[str, Any]]:
        """Fetch raw records from public API, web feed, or structured cache."""
        pass

    @abstractmethod
    def normalize_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw external payload into normalized CareAtZero record schema."""
        pass

    def get_source_metadata(self, last_checked: str) -> Dict[str, Any]:
        return {
            "id": self.source_id,
            "name": self.name,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "last_checked": last_checked,
            "status": self.status
        }
