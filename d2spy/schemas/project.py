from datetime import date, datetime
from dataclasses import dataclass
from typing import Literal, Optional, TypedDict
from uuid import UUID

from d2spy.schemas.geojson import GeoJSON


@dataclass
class Project:
    id: UUID
    deactivated_at: Optional[datetime]
    description: str
    field: GeoJSON
    flight_count: int
    harvest_date: Optional[date]
    is_active: bool
    location_id: UUID
    planting_date: Optional[date]
    role: Literal["owner", "manager", "viewer"]
    team_id: Optional[UUID]
    title: str

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(
            id=data["id"],
            deactivated_at=data["deactivated_at"],
            description=data["description"],
            field=data["field"],
            flight_count=data["flight_count"],
            harvest_date=data["harvest_date"],
            is_active=data["is_active"],
            location_id=data["location_id"],
            planting_date=data["planting_date"],
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
    flight_count: int
    role: Literal["owner", "manager", "viewer"]
    title: str

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(
            id=data["id"],
            centroid=data["centroid"],
            description=data["description"],
            flight_count=data["flight_count"],
            role=data["role"],
            title=data["title"],
        )
