from datetime import date, datetime
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional, TypedDict
from uuid import UUID

from d2spy.schemas.geojson import ProjectBoundaryGeoJSON


@dataclass
class Project:
    id: UUID
    deactivated_at: Optional[datetime]
    description: str
    field: ProjectBoundaryGeoJSON
    flight_count: int
    end_date: Optional[date]
    is_active: bool
    location_id: UUID
    start_date: Optional[date]
    role: Literal["owner", "manager", "viewer"]
    team_id: Optional[UUID]
    title: str

    @classmethod
    def from_dict(cls, data: Dict[Any, Any]) -> "Project":
        start_date = data.get("start_date") or data.get("planting_date")
        start_date_deserialized = (
            datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(start_date, str)
            else None
        )

        end_date = data.get("end_date") or data.get("harvest_date")
        end_date_deserialized = (
            datetime.strptime(end_date, "%Y-%m-%d").date()
            if isinstance(end_date, str)
            else None
        )

        return cls(
            id=data["id"],
            deactivated_at=data["deactivated_at"],
            description=data["description"],
            field=data["field"],
            flight_count=data["flight_count"],
            end_date=end_date_deserialized,
            is_active=data["is_active"],
            location_id=data["location_id"],
            start_date=start_date_deserialized,
            role=data["role"],
            team_id=data["team_id"],
            title=data["title"],
        )


class Centroid(TypedDict):
    x: float
    y: float


@dataclass
class MultiProject:
    id: UUID
    centroid: Centroid
    description: str
    end_date: Optional[date]
    flight_count: int
    role: Literal["owner", "manager", "viewer"]
    start_date: Optional[date]
    title: str

    @classmethod
    def from_dict(cls, data: dict) -> "MultiProject":
        start_date = data.get("start_date") or data.get("planting_date")
        start_date_deserialized = (
            datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(start_date, str)
            else None
        )

        end_date = data.get("end_date") or data.get("harvest_date")
        end_date_deserialized = (
            datetime.strptime(end_date, "%Y-%m-%d").date()
            if isinstance(end_date, str)
            else None
        )

        return cls(
            id=data["id"],
            centroid=data["centroid"],
            description=data["description"],
            end_date=end_date_deserialized,
            flight_count=data["flight_count"],
            role=data["role"],
            start_date=start_date_deserialized,
            title=data["title"],
        )
