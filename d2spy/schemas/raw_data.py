from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Optional
from uuid import UUID


@dataclass
class RawData:
    id: UUID
    filepath: str
    original_filename: str
    is_active: bool
    flight_id: UUID
    deactivated_at: Optional[datetime]
    status: str
    url: str

    @classmethod
    def from_dict(cls, data: Dict) -> "RawData":
        return cls(
            id=data["id"],
            filepath=data["filepath"],
            original_filename=data["original_filename"],
            is_active=data["is_active"],
            flight_id=data["flight_id"],
            deactivated_at=data["deactivated_at"],
            status=data["status"],
            url=data["url"],
        )
