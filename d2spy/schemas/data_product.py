from datetime import date, datetime
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from d2spy.schemas.stac_properties import STACProperties


@dataclass
class DataProduct:
    id: UUID
    data_type: str
    filepath: str
    original_filename: str
    is_active: bool
    flight_id: UUID
    deactivated_at: Optional[datetime]
    public: bool
    stac_properties: STACProperties
    status: str
    url: str

    @classmethod
    def from_dict(cls, data: dict) -> "DataProduct":
        return cls(
            id=data["id"],
            data_type=data["data_type"],
            filepath=data["filepath"],
            original_filename=data["original_filename"],
            is_active=data["is_active"],
            flight_id=data["flight_id"],
            deactivated_at=data["deactivated_at"],
            public=data["public"],
            stac_properties=data["stac_properties"],
            status=data["status"],
            url=data["url"],
        )
