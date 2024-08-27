from datetime import date, datetime
from dataclasses import dataclass
from typing import Dict, List, Optional
from uuid import UUID

from d2spy.schemas.data_product import DataProduct


@dataclass
class Flight:
    id: UUID
    name: Optional[str]
    acquisition_date: date
    altitude: float
    side_overlap: float
    forward_overlap: float
    sensor: str
    platform: str
    is_active: bool
    deactivated_at: Optional[datetime]
    project_id: UUID
    pilot_id: UUID
    data_products: List[DataProduct]

    @classmethod
    def from_dict(cls, data: Dict) -> "Flight":
        return cls(
            id=data["id"],
            name=data["name"],
            acquisition_date=data["acquisition_date"],
            altitude=data["altitude"],
            side_overlap=data["side_overlap"],
            forward_overlap=data["forward_overlap"],
            sensor=data["sensor"],
            platform=data["platform"],
            is_active=data["is_active"],
            deactivated_at=data["deactivated_at"],
            project_id=data["project_id"],
            pilot_id=data["pilot_id"],
            data_products=data["data_products"],
        )
