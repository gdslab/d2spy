from typing import List, TypedDict
from uuid import UUID


class Geometry(TypedDict):
    type: str
    coordinates: List[List[List[float]]]


class Properties(TypedDict):
    id: UUID
    center_x: float
    center_y: float


class GeoJSON(TypedDict):
    type: str
    geometry: Geometry
    properties: Properties
