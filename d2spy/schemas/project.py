from datetime import date, datetime
from dataclasses import dataclass
from typing import Literal, Optional, TypedDict
from uuid import UUID

from d2spy.schemas.geojson import GeoJSON


@dataclass
class Project:
    id: UUID
    title: str
    description: str
    planting_date: Optional[date]
    harvest_date: Optional[date]
    is_active: bool
    location_id: UUID
    team_id: UUID
    deactivated_at: Optional[datetime]
    owner_id: UUID
    is_owner: bool
    field: GeoJSON
    flight_count: int

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            planting_date=data["planting_date"],
            harvest_date=data["harvest_date"],
            is_active=data["is_active"],
            location_id=data["location_id"],
            team_id=data["team_id"],
            deactivated_at=data["deactivated_at"],
            owner_id=data["owner_id"],
            is_owner=data["is_owner"],
            field=data["field"],
            flight_count=data["flight_count"],
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
